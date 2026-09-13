@echo off
title AgriSmart AI - Dependency Installer
color 0E
cls
echo =====================================================================
echo               Installing AgriSmart AI Dependencies
echo =====================================================================
echo.
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo All packages installed successfully!
pause
