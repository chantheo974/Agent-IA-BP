"""Secrets/settings and provider boundary tests; no real API key required."""
import base64
import json
import os
from pathlib import Path
import tempfile
import unittest

import httpx

from tca_bp.web_settings import (DEFAULT_MODEL, ProviderError, WebSettings,
                                 WindowsSecretProtector)


class TestProtector:
    """Portable test double; production never selects this implementation."""
    def protect(self, text):
        return base64.b64encode(text[::-1].encode()).decode()

    def unprotect(self, text):
        return base64.b64decode(text).decode()[::-1]


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "private" / "settings.json"
        self.settings = WebSettings(self.path, protector=TestProtector())

    def test_default_and_missing_key(self):
        self.assertEqual(self.settings.public()["model"], DEFAULT_MODEL)
        self.assertFalse(self.settings.public()["api_key_configured"])
        self.assertFalse(self.path.exists())
        with self.assertRaises(ProviderError) as error:
            self.settings.credentials()
        self.assertEqual(error.exception.code, "API_KEY_REQUIRED")

    def test_secret_not_public_or_cleartext_and_blank_preserves(self):
        public = self.settings.update(api_key="fake-secret-unit-test")
        self.assertTrue(public["api_key_configured"])
        self.assertNotIn("fake-secret", json.dumps(public))
        self.assertNotIn("fake-secret", self.path.read_text(encoding="utf-8"))
        self.assertNotIn("fake-secret", repr(self.settings.credentials()))
        self.settings.update(api_key="", model="deepseek-v4-flash")
        self.assertEqual(self.settings.credentials().api_key, "fake-secret-unit-test")
        self.settings.update(clear_api_key=True)
        self.assertFalse(self.settings.public()["api_key_configured"])

    def test_validation_never_partially_writes(self):
        self.settings.update(api_key="old-secret")
        original = self.path.read_bytes()
        for url in ("http://api.example.com", "https://user:password@example.com", "https://example.com?key=secret",
                    "https://example.com#token", "https://example.com bad", "file:///tmp/model", "https://localhost:999999"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.settings.update(base_url=url, api_key="new-secret")
            self.assertEqual(self.path.read_bytes(), original)
        with self.assertRaises(ValueError):
            self.settings.update(model="model\nAuthorization: secret")
        with self.assertRaises(ValueError):
            self.settings.update(clear_api_key=True, api_key="both")

    def test_loopback_http_and_configurable_model(self):
        self.settings.update(base_url="http://127.0.0.1:9200/v1/", model="local/model:latest")
        self.assertEqual(self.settings.public()["base_url"], "http://127.0.0.1:9200/v1")
        self.settings.update(base_url="http://[::1]:9200")
        self.assertEqual(self.settings.public()["model"], "local/model:latest")

    def test_models_call_uses_saved_key_and_never_returns_it(self):
        self.settings.update(api_key="secret-for-models")
        def handler(request):
            self.assertEqual(request.url.path, "/models")
            self.assertEqual(request.headers["authorization"], "Bearer secret-for-models")
            return httpx.Response(200, json={"data": [{"id": DEFAULT_MODEL}, {"id": "other-model"}]})
        result = self.settings.test_connection(transport=httpx.MockTransport(handler))
        self.assertTrue(result["model_available"])
        self.assertNotIn("secret", json.dumps(result))

    def test_provider_errors_redact_body_and_headers(self):
        self.settings.update(api_key="secret-never-log")
        for status, retryable in ((401, False), (429, True), (502, True)):
            with self.subTest(status=status):
                transport = httpx.MockTransport(lambda req: httpx.Response(status, text="Oops secret-never-log " + req.headers["authorization"]))
                with self.assertRaises(ProviderError) as caught:
                    self.settings.test_connection(transport=transport)
                self.assertNotIn("secret", str(caught.exception))
                self.assertEqual(caught.exception.retryable, retryable)

    def test_redirect_does_not_forward_api_key(self):
        self.settings.update(api_key="redirect-secret")
        calls = []
        def handler(request):
            calls.append(str(request.url))
            return httpx.Response(302, headers={"location": "https://other-provider.example/steal"})
        with self.assertRaises(ProviderError):
            self.settings.test_connection(transport=httpx.MockTransport(handler))
        self.assertEqual(len(calls), 1)

    @unittest.skipUnless(os.name == "nt", "DPAPI is Windows-native")
    def test_real_windows_dpapi_round_trip(self):
        protector = WindowsSecretProtector()
        cipher = protector.protect("dummy-key-no-provider-access")
        self.assertNotIn("dummy-key", cipher)
        self.assertEqual(protector.unprotect(cipher), "dummy-key-no-provider-access")
        # Exercise the actual caller too, including a fresh settings instance.
        settings=WebSettings(self.path,protector=protector)
        settings.update(api_key='dummy-key-no-provider-access')
        reloaded=WebSettings(self.path)
        self.assertTrue(reloaded.public()['api_key_configured'])
        self.assertNotIn('dummy-key',self.path.read_text(encoding='utf-8'))
        self.assertEqual(reloaded.credentials().api_key,'dummy-key-no-provider-access')


if __name__ == "__main__":
    unittest.main()
