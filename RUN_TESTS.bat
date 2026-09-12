@echo off
title AgriSmart AI - Test Suite Runner
color 0B
cls
echo =====================================================================
echo              AgriSmart AI - Automated Test Suite Runner
echo =====================================================================
echo.
python -m unittest discover -s tests
echo.
echo =====================================================================
pause
