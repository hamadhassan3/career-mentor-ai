#!/bin/bash

# Unix/Mac shell script to apply resume parser patch
echo "Resume Parser Patch Application (Unix/Mac)"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python command: $PYTHON_CMD"

# Make the Python script executable if needed
chmod +x apply_resume_parser_patch.py

# Run the patch application script
echo "Running patch application script..."
$PYTHON_CMD apply_resume_parser_patch.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "Patch application completed successfully."
else
    echo ""
    echo "Patch application failed. Please check the errors above."
    exit 1
fi