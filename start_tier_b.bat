@echo off
rem Tier B as deployed (Vulkan, Qwen3.5-4B Q4_K_M + lora_4b adapter), in Kiosk mode.
rem App on port 8002, llama-server on port 8082, logs in logs\tier_b; restarted if it stops.
rem   start_tier_b.bat           a window on the right half of the screen
rem   start_tier_b.bat kiosk     full-screen, locked, as in a store (Alt+F4 closes the browser)
rem   start_tier_b.bat left, right or centre     where the window goes
setlocal EnableExtensions
cd /d "%~dp0"
call "%~dp0scripts\_env.bat"
if errorlevel 1 exit /b 1
set "VIEW=--windowed --window right"
if /i "%~1"=="left" set "VIEW=--windowed --window left"
if /i "%~1"=="right" set "VIEW=--windowed --window right"
if /i "%~1"=="centre" set "VIEW=--windowed --window centre"
if /i "%~1"=="kiosk" set "VIEW="
title Kiosk - Tier B - http://127.0.0.1:8002
echo.
echo  Tier B kiosk at http://127.0.0.1:8002   (Ctrl+C or closing this window stops it)
echo  Logs: logs\tier_b
echo.
"%VPY%" app\kiosk_launcher.py --tier B --port 8002 --llama-port 8082 --log-dir logs\tier_b %VIEW%
if errorlevel 1 pause
