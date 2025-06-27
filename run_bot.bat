@echo off
echo Starting Esoteric Content Bot...
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% neq 0 (
    echo Error occurred during execution. Check logs for details.
    pause
) else (
    echo Bot completed successfully!
)