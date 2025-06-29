@echo off
echo Starting Esoteric Content Generator (Manual Upload Mode)...
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% neq 0 (
    echo Error occurred during content generation. Check logs for details.
    pause
) else (
    echo Content generation completed successfully!
    echo Check the ready_to_upload folder for new videos.
    echo Run "python upload_manager.py" to manage uploads.
)