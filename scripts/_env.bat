@echo off
rem Shared by the start scripts: the virtual environment's Python, and where llama.cpp and the models are.
set "REPO=%~dp0.."
set "VPY=%REPO%\.venv\Scripts\python.exe"
set "SLM_BASE_DIR=%REPO%\runtime"
if exist "%VPY%" exit /b 0
echo.
echo  This copy is not set up yet. Double-click setup.bat first.
echo.
pause
exit /b 1
