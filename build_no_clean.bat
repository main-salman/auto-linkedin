@echo off
echo Building Auto-LinkedIn executable for Windows (without cleaning)...
python build_no_clean.py
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)
echo Build completed successfully!
pause 