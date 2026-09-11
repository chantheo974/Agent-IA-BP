@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
  start "TCA BP" ".venv\Scripts\pythonw.exe" -m tca_bp gui
) else (
  py -3.14 -m tca_bp gui
)
