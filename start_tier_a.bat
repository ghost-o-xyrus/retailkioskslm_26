@echo off
rem Tier A as deployed (CPU, Qwen3.5-2B Q8_0, Objective 3 pipeline), in Kiosk mode.
rem App on port 8001, llama-server on port 8081, logs in logs\tier_a; restarted if it stops.
rem   start_tier_a.bat           a window on the left half of the screen
rem   start_tier_a.bat kiosk     full-screen, locked, as in a store (Alt+F4 closes the browser)
rem   start_tier_a.bat left, right or centre     where the window goes
setlocal EnableExtensions
cd /d "%~dp0"
call "%~dp0scripts\_env.bat"
if errorlevel 1 exit /b 1
set "VIEW=--windowed --window left"
if /i "%~1"=="left" set "VIEW=--windowed --window left"
if /i "%~1"=="right" set "VIEW=--windowed --window right"
if /i "%~1"=="centre" set "VIEW=--windowed --window centre"
if /i "%~1"=="kiosk" set "VIEW="
title Kiosk - Tier A - http://127.0.0.1:8001
echo.
echo  Tier A kiosk at http://127.0.0.1:8001   (Ctrl+C or closing this window stops it)
echo  Logs: logs\tier_a
echo.
"%VPY%" app\kiosk_launcher.py --tier A --port 8001 --llama-port 8081 --log-dir logs\tier_a %VIEW%
if errorlevel 1 pause
