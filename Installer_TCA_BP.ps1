$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& py -3.14 -c "import sys, tkinter; assert sys.version_info >= (3,14); print(sys.version)"
if ($LASTEXITCODE -ne 0) { throw 'Installer Python 3.14 avec Tcl/Tk avant de continuer.' }
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { & py -3.14 -m venv .venv }
if ($LASTEXITCODE -ne 0) { throw 'Création de l''environnement Python interrompue.' }
& '.venv\Scripts\python.exe' -c "import sys, tkinter; assert sys.version_info >= (3,14), 'Python 3.14 requis dans .venv'"
if ($LASTEXITCODE -ne 0) { throw 'L''environnement .venv existant doit utiliser Python 3.14 avec Tcl/Tk.' }
& '.venv\Scripts\python.exe' -m pip install -e .
if ($LASTEXITCODE -ne 0) { throw 'Installation des dépendances interrompue.' }
& '.venv\Scripts\python.exe' -m tca_bp doctor
if ($LASTEXITCODE -ne 0) { throw 'Diagnostic de l''installation interrompu.' }
Write-Output 'Lancer ensuite Lancer_TCA_BP.cmd. Le pack inclut sa trame ; une reconstruction depuis le dépôt seul nécessite les références locales.'
