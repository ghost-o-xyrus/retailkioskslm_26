@echo off
rem Lab mode: every setup of Objectives 1 to 5, both models, compare view, stage and tool drawers.
rem App on port 8000, llama-server on port 8080. Offline: any connection leaving this computer is refused and logged.
setlocal EnableExtensions
cd /d "%~dp0"
call "%~dp0scripts\_env.bat"
if errorlevel 1 exit /b 1
title Kiosk assistant - Lab mode - http://127.0.0.1:8000
echo.
echo  Lab mode at http://127.0.0.1:8000   (Ctrl+C or closing this window stops it)
echo  Logs: logs\lab
echo.
"%VPY%" app\server.py --mode lab --tier A --port 8000 --llama-port 8080 --offline --open --log-dir logs\lab --net-log logs\lab\offline_guard.jsonl %*
if errorlevel 1 pause
