@echo off
echo Packaging Auto-LinkedIn for distribution (improved method)...
python improved_packaging.py
if errorlevel 1 (
    echo Packaging failed!
    pause
    exit /b 1
)
echo Packaging completed successfully!
echo The distributable package is in the 'packages' folder.
pause 