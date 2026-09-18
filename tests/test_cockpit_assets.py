"""Static cockpit assets must be served as assets, never as an HTML fallback."""
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient
from tca_bp.service import Application
from tca_bp.web_server import create_app
from tca_bp.web_workspace import WebWorkspace
from tests.test_service import FakeEngine


class CockpitAssetsTests(unittest.TestCase):
    def test_local_icons_direct_routes_and_missing_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            frontend=root/'frontend/dist'
            (frontend/'icone').mkdir(parents=True)
            (frontend/'index.html').write_text('<html lang="fr">Cockpit</html>',encoding='utf-8')
            svg='<svg xmlns="http://www.w3.org/2000/svg"><symbol id="check"/></svg>'
            (frontend/'icone/iconoir-sprite.svg').write_text(svg,encoding='utf-8')
            (frontend/'favicon.svg').write_text(svg,encoding='utf-8')
            service=Application(root,root/'data',engine=FakeEngine(root))
            workspace=WebWorkspace(service)
            try:
                with TestClient(create_app(service,workspace=workspace,start_jobs=False),base_url='http://127.0.0.1:8765') as client:
                    for path in ('/icone/iconoir-sprite.svg','/favicon.svg'):
                        result=client.get(path)
                        self.assertEqual(result.status_code,200,result.text)
                        self.assertEqual(result.text,svg)
                        self.assertTrue(result.headers['content-type'].startswith('image/svg+xml'))
                    self.assertEqual(client.get('/icone/absent.svg').status_code,404)
                    self.assertEqual(client.get('/api/unknown').status_code,404)
                    for path in ('/demo/parcours','/expert/feuilles/sheet_05','/simulations/scenario_1'):
                        self.assertEqual(client.get(path).text,'<html lang="fr">Cockpit</html>')
                    self.assertEqual(client.get('/icone/%2e%2e/%2e%2e/pyproject.toml').status_code,404)
            finally:
                workspace.close()
