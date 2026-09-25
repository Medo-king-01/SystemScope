@echo off
REM SystemScope Launcher
setlocal
set VENV=D:\\Programs\\venvs\\systemscope
set PROJECT=D:\\Projects\\SystemScope
call %VENV%\\Scripts\\activate.bat
set QT_PLUGIN_PATH=%VENV%\\Lib\\site-packages\\PySide6\\Qt5\\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=%VENV%\\Lib\\site-packages\\PySide6\\Qt5\\plugins\\platforms
set QT_QUICK_BACKEND=software
%PROJECT%\\dist\\SystemScope\\SystemScope.exe