"""Install the pinned local Windows OCR runtime, outside the project and Git.

Usage: py -3.14 tools/install_ocr.py [--check]
Downloads are HTTPS, pinned SHA256, no source document leaves the machine.
The installer runs as the current user, silently, without changing PATH.
An existing incomplete/different directory is refused rather than overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request

VERSION = "5.5.3.20260724"
INSTALLER_URL = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.3/tesseract-ocr-w64-setup-5.5.3.20260724.exe"
INSTALLER_SHA256 = "bee9e3434bd94fd65387d9be28cd467a41f61b1275383b55b0f59a1331270ae4"
EXECUTABLE_SHA256 = "c66f0f12ed76f6aa455dac97684bbc86756d6a732380bee09122454cfda3f420"
TESSDATA_COMMIT = "87416418657359cb625c412a48b6e1d6d41c29bd"
MODEL_HASHES = {"fra": "ced037562e8c80c13122dece28dd477d399af80911a28791a66a63ac1e3445ca",
                "eng": "7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2"}


def runtime_path() -> Path:
    if os.name != "nt" or not os.environ.get("LOCALAPPDATA"):
        raise RuntimeError("Cet installateur concerne Windows et le compte utilisateur courant")
    return Path(os.environ["LOCALAPPDATA"]).resolve() / "TCA_BP/runtimes/tesseract"


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inspect_runtime(target: Path) -> dict:
    target = Path(target)
    expected = {"tesseract.exe": EXECUTABLE_SHA256,
                **{f"tessdata/{lang}.traineddata": digest for lang, digest in MODEL_HASHES.items()}}
    files = []
    for relative, digest in expected.items():
        path = target / relative
        actual = _sha(path) if path.is_file() and not path.is_symlink() else None
        files.append({"path": relative, "sha256": actual, "expected_sha256": digest, "matches": actual == digest})
    return {"status": "READY" if all(f["matches"] for f in files) else "ABSENT_OR_DIFFERENT",
            "version": VERSION, "path": str(target), "languages": ["fra", "eng"], "files": files}


def _download(url: str, target: Path, expected_sha256: str):
    request = urllib.request.Request(url, headers={"User-Agent": "TCA-BP-local-OCR-installer/0.4"})
    digest, size = hashlib.sha256(), 0
    with urllib.request.urlopen(request, timeout=60) as response, target.open("xb") as stream:
        if not response.geturl().startswith("https://"):
            raise RuntimeError("Redirection hors HTTPS refusée")
        while chunk := response.read(1024 * 1024):
            size += len(chunk)
            if size > 100 * 1024 * 1024:
                raise RuntimeError("Téléchargement trop volumineux")
            digest.update(chunk)
            stream.write(chunk)
    if digest.hexdigest() != expected_sha256:
        raise RuntimeError("Empreinte SHA256 du téléchargement incompatible")


def install() -> dict:
    target = runtime_path()
    current = inspect_runtime(target)
    if current["status"] == "READY":
        return {**current, "already_installed": True}
    if target.exists():
        raise RuntimeError("Le dossier OCR existe avec un contenu incomplet ou différent. Aucun remplacement automatique. Conserver ce dossier et résoudre explicitement son état avant de réessayer.")
    with tempfile.TemporaryDirectory(prefix="tca-ocr-install-") as temp:
        temp = Path(temp)
        installer = temp / "setup.exe"
        _download(INSTALLER_URL, installer, INSTALLER_SHA256)
        for language, digest in MODEL_HASHES.items():
            _download(f"https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/{TESSDATA_COMMIT}/{language}.traineddata",
                      temp / f"{language}.traineddata", digest)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError("Un autre processus a créé le dossier OCR")
        environment = os.environ.copy()
        environment["__COMPAT_LAYER"] = "RunAsInvoker"
        # NSIS /D must be the last argument and takes the remainder, unquoted.
        command = f'"{installer}" /S /CURRENTUSER /D={target}'
        result = subprocess.run(command, env=environment, timeout=180, check=False,
                                creationflags=0x08000000, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Installation OCR échouée ({result.returncode}); le dossier partiel reste identifiable")
        if not (target / "tesseract.exe").is_file() or _sha(target / "tesseract.exe") != EXECUTABLE_SHA256:
            raise RuntimeError("Exécutable installé absent ou incompatible")
        for language in MODEL_HASHES:
            destination = target / "tessdata" / f"{language}.traineddata"
            destination.write_bytes((temp / f"{language}.traineddata").read_bytes())
        installed = inspect_runtime(target)
        if installed["status"] != "READY":
            raise RuntimeError("Contrôle du runtime OCR installé échoué")
        check = subprocess.run([str(target / "tesseract.exe"), "--tessdata-dir", str(target / "tessdata"), "--list-langs"],
                               capture_output=True, text=True, timeout=20, creationflags=0x08000000, check=False)
        if check.returncode or not all(lang in check.stdout.splitlines() for lang in MODEL_HASHES):
            raise RuntimeError("Les modèles OCR requis ne sont pas opérationnels")
        receipt = {**installed, "already_installed": False, "installer_url": INSTALLER_URL,
                   "installer_sha256": INSTALLER_SHA256, "tessdata_commit": TESSDATA_COMMIT,
                   "scope": "CURRENT_USER", "path_environment_changed": False}
        (target / "tca_install_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Contrôle local sans téléchargement ni écriture")
    args = parser.parse_args(argv)
    try:
        result = inspect_runtime(runtime_path()) if args.check else install()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "READY" else 1
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "ERROR", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
