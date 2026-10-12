@echo off
cd /d "%~dp0"
echo Dang khoi chay chuong trinh...
.\.venv\Scripts\python.exe main.py %*
pause
