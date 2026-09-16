@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0.."

if "%~1"=="" (
  echo ERROR: usage: tools\validate-candidate.cmd ^<expected-40-char-sha^> 1>&2
  exit /b 2
)

set "EXPECTED_SHA=%~1"
set "ACTUAL_SHA="

echo [ RUN] exact-head
for /f "usebackq delims=" %%I in (`git rev-parse HEAD 2^>nul`) do set "ACTUAL_SHA=%%I"
if not defined ACTUAL_SHA (
  echo ERROR: unable to resolve Git HEAD. 1>&2
  exit /b 1
)
if /i not "%ACTUAL_SHA%"=="%EXPECTED_SHA%" (
  echo ERROR: candidate HEAD mismatch. 1>&2
  echo        expected: %EXPECTED_SHA% 1>&2
  echo        actual:   %ACTUAL_SHA% 1>&2
  exit /b 1
)
echo [ OK ] exact-head %ACTUAL_SHA%

echo [ RUN] bootstrap
call tools\bootstrap.cmd
if errorlevel 1 (
  echo [FAIL] bootstrap 1>&2
  exit /b 1
)
echo [ OK ] bootstrap

echo [ RUN] full-tests
call tools\test.cmd
if errorlevel 1 (
  echo [FAIL] full-tests 1>&2
  exit /b 1
)
echo [ OK ] full-tests

echo [ RUN] diff-check
git diff --check
if errorlevel 1 (
  echo [FAIL] diff-check 1>&2
  exit /b 1
)
git diff --cached --check
if errorlevel 1 (
  echo [FAIL] cached-diff-check 1>&2
  exit /b 1
)
echo [ OK ] diff-check

echo [ RUN] clean-tree
set "DIRTY_TREE="
for /f "delims=" %%I in ('git status --porcelain --untracked-files^=all') do set "DIRTY_TREE=1"
if defined DIRTY_TREE (
  echo ERROR: candidate validation changed or found tracked/untracked repository state: 1>&2
  git status --short
  exit /b 1
)
echo [ OK ] clean-tree

echo [ RUN] exact-head-final
set "FINAL_SHA="
for /f "usebackq delims=" %%I in (`git rev-parse HEAD 2^>nul`) do set "FINAL_SHA=%%I"
if /i not "%FINAL_SHA%"=="%EXPECTED_SHA%" (
  echo ERROR: HEAD changed during validation. 1>&2
  echo        expected: %EXPECTED_SHA% 1>&2
  echo        actual:   %FINAL_SHA% 1>&2
  exit /b 1
)
echo [ OK ] exact-head-final %FINAL_SHA%

echo.
echo [ OK ] Context candidate validation PASS
exit /b 0
