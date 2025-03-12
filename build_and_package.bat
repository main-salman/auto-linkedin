@echo off
echo Building and Packaging Auto-LinkedIn...

REM First try to clean up any potential locked files
echo Attempting to clean up build folders...
powershell -Command "Get-Process | Where-Object {$_.ProcessName -eq 'Auto-LinkedIn'} | Stop-Process -Force -ErrorAction SilentlyContinue"

REM Ensure all Python processes are stopped as they may be locking files
powershell -Command "Get-Process | Where-Object {$_.ProcessName -eq 'python'} | Stop-Process -Force -ErrorAction SilentlyContinue"

REM Try to delete any locked directories
echo Cleaning build directories...
if exist dist (
    rd /s /q dist 2>nul
    if exist dist (
        echo Warning: Could not remove dist directory. Continuing anyway...
    ) else (
        echo Cleaned dist directory.
    )
)

if exist build (
    rd /s /q build 2>nul
    if exist build (
        echo Warning: Could not remove build directory. Continuing anyway...
    ) else (
        echo Cleaned build directory.
    )
)

REM Build the executable using the no-clean version
echo Building executable...
python build_no_clean.py
if errorlevel 1 (
    echo Build failed! Attempting to create package with template files...
    goto CreateTemplatePackage
)

REM Package the application
echo Packaging application...
python improved_packaging.py
if errorlevel 1 (
    echo Packaging failed! Attempting to create package with template files...
    goto CreateTemplatePackage
)

echo Build and packaging completed successfully!
echo The executable is in the 'dist' folder.
echo The distributable package is in the 'packages' folder.
goto End

:CreateTemplatePackage
echo Creating template package without executable...
call create_package.bat
if errorlevel 1 (
    echo Failed to create template package!
    pause
    exit /b 1
)

:End
pause 