"""Real pipe EOF and delayed cleanup, without creating any Excel process."""
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock

from tca_bp.native_cleanup import finish_native_process


class NativeCleanupTests(unittest.TestCase):
    def test_eof_before_ownership_allows_delayed_worker_to_clean_itself(self):
        with tempfile.TemporaryDirectory() as directory:
            proof=Path(directory)/'cleaned.txt'
            script='import sys,time;from pathlib import Path;time.sleep(.15);assert sys.stdin.readline()=="";Path(sys.argv[1]).write_text("cleaned");'
            process=subprocess.Popen([sys.executable,'-c',script,str(proof)],stdin=subprocess.PIPE,
                                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,text=True)
            finish_native_process(process,None,False,grace_seconds=.01)
            process.wait(timeout=5)
            self.assertEqual(process.returncode,0)
            self.assertEqual(proof.read_text(),'cleaned')

    def test_only_known_handle_is_terminated_even_when_wait_fails(self):
        process=Mock();process.poll.return_value=None;process.stdin.closed=False
        owned=Mock()
        finish_native_process(process,owned,False)
        process.stdin.close.assert_called_once()
        owned.terminate.assert_called_once();owned.close.assert_called_once()
        process.kill.assert_called_once()


if __name__=='__main__':unittest.main()
