@echo off
chcp 65001 >nul
setlocal
cd /d "D:\AIAGENT应用\replace_txt\notepad"
set "PATH=%CD%\.venv\Scripts;%PATH%"
python main.py
if errorlevel 1 pause
endlocal
