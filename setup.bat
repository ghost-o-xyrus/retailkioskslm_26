@echo off
rem One-click setup: Python 3.13 if missing, a virtual environment, llama.cpp, the models; then Lab mode opens.
rem Run it again at any time: finished steps are skipped and interrupted downloads resume.
rem Options are passed on to scripts\fetch_assets.py, for example:  setup.bat --only tier-a
setlocal EnableExtensions
cd /d "%~dp0"
title Kiosk assistant - setup

echo.
echo  Offline kiosk assistant: setup
echo  ------------------------------
echo  1. Python 3.13, if this computer has no Python 3.10 to 3.13
echo  2. A virtual environment in this folder (.venv) with four packages
echo  3. llama.cpp (CPU and Vulkan builds), the two models, the retrieval models
echo     and the adapters: about 6 GB of downloads, kept in this folder
echo  Then Lab mode opens in your browser.
echo.

if not exist ".venv\Scripts\python.exe" goto :need_python
set "PY=%~dp0.venv\Scripts\python.exe"
goto :run

:need_python
call :find_python
if defined PY goto :run
echo  No Python 3.10 to 3.13 found. Installing Python 3.13 with winget ...
where winget >nul 2>nul
if errorlevel 1 goto :no_winget
winget install -e --id Python.Python.3.13 --scope user --accept-package-agreements --accept-source-agreements
if errorlevel 1 winget install -e --id Python.Python.3.13 --accept-package-agreements --accept-source-agreements
call :find_python
if defined PY goto :run
goto :no_python

:run
echo  Python: "%PY%"
"%PY%" "%~dp0scripts\setup_kiosk.py" %*
if errorlevel 1 goto :failed
echo.
echo  Setup finished.
if /i "%SLM_NO_START%"=="1" goto :done
echo  Starting Lab mode (start_lab.bat) ...
echo.
call "%~dp0start_lab.bat"
goto :done

:no_winget
echo.
echo  winget is not available on this computer, so Python cannot be installed
echo  automatically. Install Python 3.13 from https://www.python.org/downloads/
echo  (tick "Add python.exe to PATH"), then double-click setup.bat again.
echo.
pause
exit /b 1

:no_python
echo.
echo  Python 3.13 was installed but cannot be found from this window.
echo  Close this window and double-click setup.bat again.
echo.
pause
exit /b 1

:failed
echo.
echo  Setup did not finish. The lines above say which step stopped.
echo  Fix that (most often the internet connection) and run setup.bat again:
echo  it continues where it stopped.
echo.
pause
exit /b 1

:done
endlocal
exit /b 0

rem ---------------------------------------------------------------------------
:find_python
set "PY="
call :try_launcher 3.13
if defined PY exit /b 0
call :try_path "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if defined PY exit /b 0
call :try_path "%ProgramFiles%\Python313\python.exe"
if defined PY exit /b 0
call :try_launcher 3.12
if defined PY exit /b 0
call :try_launcher 3.11
if defined PY exit /b 0
call :try_launcher 3.10
if defined PY exit /b 0
rem a python on PATH, if it is 3.10 to 3.13 (the Microsoft Store placeholder fails this test)
python -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,13) else 1)" >nul 2>nul
if errorlevel 1 exit /b 0
for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)"') do set "PY=%%P"
exit /b 0

:try_launcher
py -%1 -c "import sys" >nul 2>nul
if errorlevel 1 exit /b 0
for /f "delims=" %%P in ('py -%1 -c "import sys; print(sys.executable)"') do set "PY=%%P"
exit /b 0

:try_path
if exist "%~1" set "PY=%~1"
exit /b 0
