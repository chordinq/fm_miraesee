@echo off
cd /d "%~dp0"
set PYTHONUTF8=1

REM import main does not load ui — check the full import graph
python -c "from ui.app import MainWindow; print('ok')" 2>run-error.log
if errorlevel 1 (
    echo Miraesee failed to start. Error log:
    type run-error.log
    pause
    exit /b 1
)

set "PYTHONW_EXE=pythonw"
for /f "delims=" %%P in ('where python 2^>nul') do (
    if exist "%%~dpPpythonw.exe" set "PYTHONW_EXE=%%~dpPpythonw.exe"
    goto :launch
)

:launch
start "" "%PYTHONW_EXE%" "%~dp0main.py" %*
