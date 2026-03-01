#!/bin/bash

echo "========================================"
echo "TalentScout Hiring Assistant"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "========================================"
echo "Starting Streamlit application..."
echo "========================================"
echo ""

streamlit run src/app.py
