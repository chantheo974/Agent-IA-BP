$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Installer Python 3.14 avant de continuer.' }
& py -3.14 -c "import sys; assert sys.version_info >= (3,14); print(sys.version)"
if ($LASTEXITCODE -ne 0) { throw 'Installer Python 3.14 avant de continuer.' }
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { & py -3.14 -m venv .venv }
if ($LASTEXITCODE -ne 0) { throw 'Création de l''environnement Python interrompue.' }
& '.venv\Scripts\python.exe' -m pip install -e .
if ($LASTEXITCODE -ne 0) { throw 'Installation des dépendances interrompue.' }
& '.venv\Scripts\python.exe' -X utf8 'tools\install_ocr.py'
if ($LASTEXITCODE -ne 0) { throw 'Installation OCR interrompue. Relancer cet installateur pour reprendre les composants manquants.' }
if (-not (Test-Path -LiteralPath 'frontend\dist\index.html')) {
    Push-Location -LiteralPath 'frontend'
    try {
        & npm.cmd ci
        if ($LASTEXITCODE -ne 0) { throw 'Installation des dépendances web interrompue.' }
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Compilation web interrompue.' }
    } finally { Pop-Location }
}
Write-Output 'Installation terminée. Ouvrir Lancer_TCA_BP_Web.cmd.'
