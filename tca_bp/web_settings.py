"""Local provider settings. Secrets are DPAPI protected for this Windows user.

Only :meth:`WebSettings.public` may be returned by an HTTP endpoint. Provider
errors deliberately omit response bodies, request headers and exception text.
"""
from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
from dataclasses import dataclass, field
import ipaddress
import json
import os
from pathlib import Path
import re
import threading
from urllib.parse import urlsplit, urlunsplit

from .storage import atomic_json


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"
MODELS = [DEFAULT_MODEL, "deepseek-flash"]


class ProviderError(RuntimeError):
    """A safe public error; no raw provider text or credentials in repr/str."""

    def __init__(self, message: str, *, code: str = "PROVIDER_ERROR", retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


@dataclass(frozen=True)
class ProviderCredentials:
    base_url: str
    model: str
    api_key: str = field(repr=False)


class _Blob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


class WindowsSecretProtector:
    """CryptProtectData, current user scope; never silently falls back to cleartext."""

    def _crypt(self, data: bytes, *, decrypt: bool) -> bytes:
        if os.name != "nt":
            raise ProviderError("Le stockage de la clé nécessite Windows DPAPI sur ce poste.", code="SECRET_STORAGE_UNAVAILABLE")
        crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        buffer = ctypes.create_string_buffer(data)
        source = _Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
        output = _Blob()
        if decrypt:
            fn = crypt32.CryptUnprotectData
            fn.argtypes = [ctypes.POINTER(_Blob), ctypes.c_void_p, ctypes.c_void_p,
                           ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_Blob)]
            second = None
        else:
            fn = crypt32.CryptProtectData
            fn.argtypes = [ctypes.POINTER(_Blob), wintypes.LPCWSTR, ctypes.c_void_p,
                           ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_Blob)]
            second = "TCA BP Web — fournisseur IA"
        fn.restype = wintypes.BOOL
        # CRYPTPROTECT_UI_FORBIDDEN, no machine-wide flag: only this user's profile.
        if not fn(ctypes.byref(source), second, None, None, None, 1, ctypes.byref(output)):
            raise ProviderError("Impossible de protéger ou de lire la clé avec le compte Windows courant.", code="SECRET_STORAGE_ERROR")
        try:
            return ctypes.string_at(output.pbData, output.cbData)
        finally:
            if output.pbData:
                ctypes.memset(output.pbData, 0, output.cbData)
                kernel32.LocalFree.argtypes = [ctypes.c_void_p]
                kernel32.LocalFree.restype = ctypes.c_void_p
                kernel32.LocalFree(output.pbData)

    def protect(self, value: str) -> str:
        return base64.b64encode(self._crypt(value.encode("utf-8"), decrypt=False)).decode("ascii")

    def unprotect(self, value: str) -> str:
        try:
            return self._crypt(base64.b64decode(value, validate=True), decrypt=True).decode("utf-8")
        except (ValueError, UnicodeError):
            raise ProviderError("Le secret enregistré est illisible. Enregistrer une nouvelle clé.", code="SECRET_STORAGE_ERROR") from None


def _base_url(value: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 2048 or any(c.isspace() for c in value):
        raise ValueError("L’adresse du fournisseur est invalide.")
    try:
        parts = urlsplit(value.rstrip("/"))
        # Accessing port also checks malformed/out-of-range ports.
        _ = parts.port
        host = parts.hostname
    except ValueError:
        raise ValueError("L’adresse du fournisseur est invalide.") from None
    if not host or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("L’adresse ne doit contenir ni identifiants, ni paramètres, ni fragment.")
    loopback = host.lower() == "localhost"
    try:
        loopback = loopback or ipaddress.ip_address(host).is_loopback
    except ValueError:
        pass
    if parts.scheme != "https" and not (parts.scheme == "http" and loopback):
        raise ValueError("Utiliser HTTPS, ou HTTP uniquement pour un fournisseur local.")
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))


def _model(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./:@+-]{0,199}", value):
        raise ValueError("L’identifiant du modèle est invalide.")
    return value


def provider_http_error(status: int) -> ProviderError:
    if status in (401, 403):
        return ProviderError("Le fournisseur refuse la clé API. Vérifier les réglages.", code="PROVIDER_AUTH")
    if status == 429:
        return ProviderError("Le fournisseur limite les requêtes. Réessayer dans quelques instants.", code="PROVIDER_RATE_LIMIT", retryable=True)
    if status >= 500 or status in (408, 409, 425):
        return ProviderError("Le fournisseur est temporairement indisponible. Le brouillon est conservé.", code="PROVIDER_UNAVAILABLE", retryable=True)
    return ProviderError(f"Le fournisseur a refusé la requête (HTTP {status}). Vérifier le modèle et l’adresse API.", code="PROVIDER_REQUEST")


class WebSettings:
    def __init__(self, path: str | Path, *, protector=None):
        self.path = Path(path).resolve()
        self._protector = protector or WindowsSecretProtector()
        self._lock = threading.RLock()

    def _read(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "base_url": DEFAULT_BASE_URL, "model": DEFAULT_MODEL}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(value, dict) or value.get("version") != 1:
                raise ValueError()
            value["base_url"] = _base_url(value["base_url"])
            value["model"] = _model(value["model"])
            if value.get("api_key_protected") and not isinstance(value["api_key_protected"], str):
                raise ValueError()
            return value
        except (ValueError, KeyError, OSError):
            raise ProviderError("Les réglages IA locaux sont illisibles.", code="SETTINGS_INVALID") from None

    def public(self) -> dict:
        with self._lock:
            value = self._read()
            return {"base_url": value["base_url"], "model": value["model"],
                    "api_key_configured": bool(value.get("api_key_protected")), "models": value.get('available_models',list(MODELS))}

    def update(self, *, base_url: str | None = None, model: str | None = None,
               api_key: str | None = None, clear_api_key: bool = False) -> dict:
        if not isinstance(clear_api_key, bool):
            raise ValueError("clear_api_key doit être un booléen.")
        if clear_api_key and api_key:
            raise ValueError("Enregistrer ou effacer la clé, pas les deux à la fois.")
        with self._lock:
            value = self._read()
            if base_url is not None:
                if _base_url(base_url)!=value['base_url']: value.pop('available_models',None)
                value["base_url"] = _base_url(base_url)
            if model is not None:
                value["model"] = _model(model)
            # A blank settings form leaves an already saved secret intact.
            if api_key:
                if not isinstance(api_key, str) or not 1 <= len(api_key) <= 4096 or any(c.isspace() for c in api_key):
                    raise ValueError("La clé API est invalide.")
                value["api_key_protected"] = self._protector.protect(api_key)
            elif api_key is not None and not isinstance(api_key, str):
                raise ValueError("La clé API doit être du texte.")
            if clear_api_key:
                value.pop("api_key_protected", None)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(self.path, value)
            if os.name != "nt":
                self.path.chmod(0o600)
            return self.public()

    def credentials(self) -> ProviderCredentials:
        with self._lock:
            value = self._read()
            if not value.get("api_key_protected"):
                raise ProviderError("Enregistrer la clé API dans les réglages pour connecter les agents.", code="API_KEY_REQUIRED")
            secret = self._protector.unprotect(value["api_key_protected"])
            return ProviderCredentials(value["base_url"], value["model"], secret)

    def test_connection(self, *, transport=None) -> dict:
        import httpx
        credentials = self.credentials()
        try:
            with httpx.Client(transport=transport, timeout=30, trust_env=False, follow_redirects=False) as client:
                response = client.get(credentials.base_url + "/models", headers={"Authorization": "Bearer " + credentials.api_key})
                if response.status_code != 200:
                    raise provider_http_error(response.status_code)
                data = response.json()
                models = [str(item["id"]) for item in data["data"] if isinstance(item, dict) and isinstance(item.get("id"), str)]
                if len(models) > 1000 or any(len(item) > 200 for item in models):
                    raise ValueError()
                with self._lock:
                    saved=self._read()
                    if saved['base_url']==credentials.base_url:
                        saved['available_models']=[_model(m) for m in models]
                        atomic_json(self.path,saved)
                return {"ok": True, "models": models, "model_available": credentials.model in models}
        except httpx.HTTPError:
            raise ProviderError("Impossible de joindre le fournisseur IA. Vérifier l’adresse et la connexion.", code="PROVIDER_NETWORK", retryable=True) from None
        except (ValueError, KeyError, TypeError):
            raise ProviderError("La liste des modèles retournée par le fournisseur est invalide.", code="PROVIDER_RESPONSE") from None
