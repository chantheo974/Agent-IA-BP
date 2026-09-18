"""Real HTTP streaming, disconnect and resume against the local ASGI server."""
import json
from pathlib import Path
import socket
import tempfile
import threading
import unittest

import httpx
import uvicorn
from tca_bp.service import Application
from tca_bp.web_server import create_app
from tca_bp.web_workspace import WebWorkspace
from tests.test_service import FakeEngine


class LiveSSETests(unittest.TestCase):
    def test_interleaved_purge_disconnect_and_old_cursor_resync(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            app=Application(root,root/'data',engine=FakeEngine(root))
            for case in ('case_a','case_b'): app.create_case('Fictif',case,case_id=case)
            work=WebWorkspace(app)
            server=None; thread=None
            try:
                work.jobs.RETAINED_EVENTS=3
                first=work.jobs.emit('case_a',data={'number':0})
                for i in range(1,6):
                    work.jobs.emit('case_a',data={'number':i})
                    work.jobs.emit('case_b',data={'number':100+i})
                self.assertEqual(len(work.jobs.events('case_b')),3)
                sock=socket.socket(); sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
                server=uvicorn.Server(uvicorn.Config(create_app(app,workspace=work,start_jobs=False),host='127.0.0.1',port=port,log_level='error'))
                thread=threading.Thread(target=lambda:server.run(sockets=[sock]),daemon=True); thread.start()
                base=f'http://127.0.0.1:{port}'
                def event(after):
                    with httpx.stream('GET',base+'/api/cases/case_a/events',headers={'Last-Event-ID':str(after)},timeout=8) as response:
                        response.raise_for_status(); lines=[]
                        for line in response.iter_lines():
                            if not line and lines: break
                            lines.append(line)
                        return dict(line.split(': ',1) for line in lines if ': ' in line)
                resumed=event(first)
                self.assertEqual(resumed['event'],'resync')
                cursor=int(resumed['id'])
                self.assertTrue(json.loads(resumed['data'])['resync_required'])
                work.jobs.emit('case_b',data={'number':999})
                newest=work.jobs.emit('case_a',data={'number':6})
                next_event=event(cursor)
                self.assertEqual(int(next_event['id']),newest)
                self.assertEqual(json.loads(next_event['data']),{'number':6})
                self.assertEqual(next_event['event'],'refresh')
                self.assertEqual(httpx.get(base+'/api/cases/case_a',timeout=8).status_code,200)
                self.assertEqual(len(work.jobs.events('case_b')),3)
            finally:
                if server: server.should_exit=True
                if thread: thread.join(timeout=10)
                work.close()
            self.assertFalse(thread.is_alive())
