@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0.."

set "EXPECTED_SHA=%~1"
set "NO_PAUSE=0"
set "FAIL_STAGE="
set "RC=1"

if /i "%~2"=="--no-pause" set "NO_PAUSE=1"
if not "%~2"=="" if /i not "%~2"=="--no-pause" (
  set "FAIL_STAGE=arguments"
  set "RC=2"
  echo ERROR: unknown option: %~2 1>&2
  goto :fail
)

if not defined EXPECTED_SHA (
  set "FAIL_STAGE=arguments"
  set "RC=2"
  echo ERROR: usage: tools\validate-candidate.cmd ^<expected-40-char-sha^> [--no-pause] 1>&2
  goto :fail
)

echo [ RUN] exact-head
set "ACTUAL_SHA="
for /f "usebackq delims=" %%I in (`git rev-parse HEAD 2^>nul`) do set "ACTUAL_SHA=%%I"
if not defined ACTUAL_SHA (
  set "FAIL_STAGE=exact-head"
  echo ERROR: unable to resolve Git HEAD. 1>&2
  goto :fail
)
if /i not "%ACTUAL_SHA%"=="%EXPECTED_SHA%" (
  set "FAIL_STAGE=exact-head"
  echo ERROR: candidate HEAD mismatch. 1>&2
  echo        expected: %EXPECTED_SHA% 1>&2
  echo        actual:   %ACTUAL_SHA% 1>&2
  goto :fail
)
echo [ OK ] exact-head %ACTUAL_SHA%

echo [ RUN] bootstrap
call tools\bootstrap.cmd
if errorlevel 1 goto :fail_bootstrap
echo [ OK ] bootstrap

echo [ RUN] full-tests
call tools\test.cmd
if errorlevel 1 goto :fail_full_tests
echo [ OK ] full-tests

echo [ RUN] diff-check
git diff --check
if errorlevel 1 goto :fail_diff_check
git diff --cached --check
if errorlevel 1 goto :fail_cached_diff_check
echo [ OK ] diff-check

echo [ RUN] clean-tree
set "DIRTY_TREE="
for /f "delims=" %%I in ('git status --porcelain --untracked-files^=all') do set "DIRTY_TREE=1"
if defined DIRTY_TREE (
  set "FAIL_STAGE=clean-tree"
  echo ERROR: candidate validation changed or found tracked/untracked repository state: 1>&2
  git status --short
  goto :fail
)
echo [ OK ] clean-tree

echo [ RUN] exact-head-final
set "FINAL_SHA="
for /f "usebackq delims=" %%I in (`git rev-parse HEAD 2^>nul`) do set "FINAL_SHA=%%I"
if /i not "%FINAL_SHA%"=="%EXPECTED_SHA%" (
  set "FAIL_STAGE=exact-head-final"
  echo ERROR: HEAD changed during validation. 1>&2
  echo        expected: %EXPECTED_SHA% 1>&2
  echo        actual:   %FINAL_SHA% 1>&2
  goto :fail
)
echo [ OK ] exact-head-final %FINAL_SHA%
goto :success

:fail_bootstrap
set "FAIL_STAGE=bootstrap"
set "RC=%errorlevel%"
goto :fail

:fail_full_tests
set "FAIL_STAGE=full-tests"
set "RC=%errorlevel%"
goto :fail

:fail_diff_check
set "FAIL_STAGE=diff-check"
set "RC=%errorlevel%"
goto :fail

:fail_cached_diff_check
set "FAIL_STAGE=cached-diff-check"
set "RC=%errorlevel%"
goto :fail

:success
echo.
echo ============================================================
echo  QIVEN CONTEXT CANDIDATE VALIDATION: PASS
echo  head : %FINAL_SHA%
echo ============================================================
echo.
if "%NO_PAUSE%"=="0" pause
endlocal & exit /b 0

:fail
if not defined FAIL_STAGE set "FAIL_STAGE=unknown"
if "%RC%"=="0" set "RC=1"
echo.
echo ============================================================ 1>&2
echo  QIVEN CONTEXT CANDIDATE VALIDATION: FAILED 1>&2
echo  stage: %FAIL_STAGE% 1>&2
echo  exit : %RC% 1>&2
echo ============================================================ 1>&2
echo.
if "%NO_PAUSE%"=="0" pause
endlocal & exit /b %RC%
