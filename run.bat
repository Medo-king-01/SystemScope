@echo off
REM SystemScope Launcher
setlocal

set VENV=D:\Programs\venvs\systemscope
set PROJECT=D:\Projects\SystemScope

call %VENV%\Scripts\activate.bat

set QT_PLUGIN_PATH=%VENV%\Lib\site-packages\PySide6\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=%VENV%\Lib\site-packages\PySide6\plugins\platforms
set QT_QUICK_BACKEND=software

cd /d %PROJECT%

echo ========================================
echo  SystemScope - Local System Intelligence
echo ========================================
echo.

%VENV%\Scripts\python.exe main.py

pause