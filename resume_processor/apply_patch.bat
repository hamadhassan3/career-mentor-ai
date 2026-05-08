@echo off
REM Windows batch script to apply resume parser patch
echo Resume Parser Patch Application (Windows)
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and add it to your system PATH
    pause
    exit /b 1
)

REM Run the patch application script
echo Running patch application script...
python apply_resume_parser_patch.py

REM Pause to see the output
if errorlevel 1 (
    echo.
    echo Patch application failed. Please check the errors above.
) else (
    echo.
    echo Patch application completed successfully.
)

pause