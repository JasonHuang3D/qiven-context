@echo off
setlocal
set "HOST_PREFLIGHT_PYTHON=C:\Env\python\3.14.7\python.exe"
if not exist "%HOST_PREFLIGHT_PYTHON%" (
  >&2 echo [FAIL] canonical Python is missing: %HOST_PREFLIGHT_PYTHON%
  exit /b 1
)
set "GIT_TERMINAL_PROMPT=0"
set "GCM_INTERACTIVE=Never"
set "GH_PROMPT_DISABLED=1"
set "PYTHONDONTWRITEBYTECODE=1"
"%HOST_PREFLIGHT_PYTHON%" "%~dp0host_preflight.py" %*
exit /b %ERRORLEVEL%
