@echo off
REM setup_and_run.bat - Windows setup script for resume processor

echo 🚀 Setting up Resume Processor...

REM Step 1: Install resume-parser
echo 📦 Installing resume-parser...
pip install resume-parser
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install resume-parser
    pause
    exit /b 1
)

REM Step 2: Install spaCy English model
echo 🔤 Installing spaCy English model...
python -m spacy download en_core_web_sm
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install spaCy model
    pause
    exit /b 1
)

REM Step 3: Fix resume-parser compatibility issues
echo 🔧 Fixing resume-parser compatibility...
python fix_resume_parser.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to fix resume-parser
    pause
    exit /b 1
)

REM Step 4: Start the server
echo 🌐 Starting Flask server...
echo Server will be available at: http://localhost:5050
echo Press Ctrl+C to stop the server
echo.
python app.py