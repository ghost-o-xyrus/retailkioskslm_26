@echo off
rem Tier A and Tier B kiosks next to each other (two windows; each loads its own model, about 8 GB of RAM together).
cd /d "%~dp0"
start "Kiosk - Tier A" /d "%~dp0." cmd /k start_tier_a.bat left
start "Kiosk - Tier B" /d "%~dp0." cmd /k start_tier_b.bat right
