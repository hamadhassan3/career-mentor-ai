#!/bin/bash
# setup_and_run.sh - macOS/Linux setup script for resume processor

echo "🚀 Setting up Resume Processor..."

# Step 1: Install resume-parser
echo "📦 Installing resume-parser..."
pip install resume-parser

# Step 2: Install spaCy English model
echo "🔤 Installing spaCy English model..."
python -m spacy download en_core_web_sm

# Step 3: Fix resume-parser compatibility issues
echo "🔧 Fixing resume-parser compatibility..."
python fix_resume_parser.py

# Step 4: Start the server
echo "🌐 Starting Flask server..."
echo "Server will be available at: http://localhost:5050"
echo "Press Ctrl+C to stop the server"
echo ""
python app.py