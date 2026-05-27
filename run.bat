@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
start "" pythonw "%~dp0main.py" %*
