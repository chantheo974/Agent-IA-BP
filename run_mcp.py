"""Lance le serveur d'outils depuis n'importe quel répertoire de travail."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from tca_bp.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main(["--project-root", str(ROOT), "mcp"]))
