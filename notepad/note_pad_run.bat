@echo off
cd /d "D:\AIAGENT应用\replace_txt\notepad"
set "PATH=%CD%\.venv\Scripts;%PATH%"
start "" pythonw main.py
