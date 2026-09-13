@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  echo ERROR: run tools\bootstrap.cmd first.
  exit /b 2
)
.venv\Scripts\python.exe tools\test.py
if errorlevel 1 exit /b %errorlevel%
.venv\Scripts\python.exe tools\test_windows_python.py
exit /b %errorlevel%
