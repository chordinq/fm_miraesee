@echo off
chcp 65001 > nul
echo Building miraesee.exe ...
pyinstaller miraesee.spec --clean
echo.
echo Done. Output: dist\miraesee.exe
