@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "_resolved="
set "_version="

if defined QIVEN_PYTHON (
  call :probe "%QIVEN_PYTHON%"
  if not defined _resolved goto :invalid_override
  goto :success
)

for /f "delims=" %%P in ('where python 2^>nul') do (
  if not defined _resolved call :probe "%%P"
)

if not defined _resolved call :probe_py

if not defined _resolved goto :not_found

:success
echo Qiven Python:
echo %_resolved%
echo Python version:
echo %_version%
endlocal & set "QIVEN_RESOLVED_PYTHON=%_resolved%" & set "QIVEN_RESOLVED_VERSION=%_version%"
exit /b 0

:invalid_override
echo ERROR: QIVEN_PYTHON does not select a working Python 3.11 or newer interpreter. 1>&2
echo QIVEN_PYTHON is an explicit selection, so no fallback was attempted. 1>&2
endlocal
exit /b 1

:not_found
echo ERROR: Python 3.11 or newer is required. 1>&2
echo Searched executable candidates returned by where python; the py launcher was tried only as a fallback. 1>&2
echo Set QIVEN_PYTHON to explicitly select a working Python 3.11 or newer interpreter. 1>&2
endlocal
exit /b 1

:probe
call "%~1" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1
if errorlevel 1 exit /b 0
for /f "delims=" %%E in ('call "%~1" -c "import sys; print(sys.executable)" 2^>nul') do if not defined _resolved set "_resolved=%%E"
for /f "delims=" %%V in ('call "%~1" -c "import sys; print('.'.join(map(str,sys.version_info[:3])))" 2^>nul') do if not defined _version set "_version=%%V"
if not defined _version set "_resolved="
exit /b 0

:probe_py
call py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1
if errorlevel 1 exit /b 0
for /f "delims=" %%E in ('call py -3 -c "import sys; print(sys.executable)" 2^>nul') do if not defined _resolved set "_resolved=%%E"
for /f "delims=" %%V in ('call py -3 -c "import sys; print('.'.join(map(str,sys.version_info[:3])))" 2^>nul') do if not defined _version set "_version=%%V"
if not defined _version set "_resolved="
exit /b 0
