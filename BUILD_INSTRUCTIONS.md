# Build Instructions for Auto-LinkedIn

These instructions will help you build distributable executables for Auto-LinkedIn.

## Prerequisites

- Python 3.9 or higher
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller (`pip install pyinstaller>=6.10.0`)

## Building on Windows

1. Run the build script by double-clicking `build_windows.bat` or running it from the command line:
   ```
   build_windows.bat
   ```

2. To create a distributable package, run:
   ```
   package_windows.bat
   ```

3. The executable will be in the `dist` folder, and the packaged ZIP file will be in the `packages` folder.

## Building on macOS/Linux

1. Make the build script executable:
   ```
   chmod +x build.py
   ```

2. Run the build script:
   ```
   ./build.py
   ```

3. Make the package script executable:
   ```
   chmod +x package.py
   ```

4. Create a distributable package:
   ```
   ./package.py
   ```

5. The executable will be in the `dist` folder, and the packaged ZIP file will be in the `packages` folder.

## Customizing the Build

You can customize the build by editing the `build.py` file. Here are some common customizations:

- Change the application name: Modify `APP_NAME` variable
- Add additional hidden imports: Add to the `pyinstaller_args` list
- Change icon: Create your own `.ico` file and update the `ICON_PATH` variable

## Troubleshooting

If you encounter issues:

1. **Missing modules**: Add them as hidden imports in the `build.py` file
2. **File not found errors**: Make sure all required files are included in the `--add-data` parameter
3. **Playwright issues**: Check that the browser installation script is working properly

## Creating Signed Packages

For distribution in app stores or to avoid security warnings:

### macOS

1. Create an Apple Developer account
2. Obtain a Developer ID certificate
3. Sign the app using:
   ```
   codesign --force --deep --sign "Developer ID Application: Your Name" "dist/Auto-LinkedIn.app"
   ```

### Windows

1. Obtain a code signing certificate from a trusted Certificate Authority
2. Sign the executable with:
   ```
   signtool sign /fd SHA256 /f cert.pfx /p password "dist\Auto-LinkedIn.exe"
   ```