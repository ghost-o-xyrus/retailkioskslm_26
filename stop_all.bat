@echo off
rem Stop every kiosk, Lab and llama-server process started from this folder.
setlocal EnableExtensions
cd /d "%~dp0"
call "%~dp0scripts\_env.bat"
if errorlevel 1 exit /b 1
"%VPY%" scripts\stop.py
pause
