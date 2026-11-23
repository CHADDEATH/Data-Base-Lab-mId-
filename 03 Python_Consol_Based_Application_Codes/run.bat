@echo off
TITLE Pak Voyage - Pakistan Tourism and Travel Management Agency
cls
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    pause
)
