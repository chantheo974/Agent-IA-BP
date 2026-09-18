@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m tca_bp.web_server %*
) else (
  py -3.14 -m tca_bp.web_server %*
)
if errorlevel 1 pause
