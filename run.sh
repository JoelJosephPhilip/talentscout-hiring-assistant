#!/bin/bash

echo "========================================"
echo "TalentScout Hiring Assistant"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "First-time setup required..."
    echo ""
    python3 setup_wizard.py
    if [ $? -ne 0 ]; then
        echo ""
        echo "Setup may have failed. Please check the errors above."
        exit 1
    fi
else
    # Check if any API key or Ollama is configured
    if ! grep -q "GROQ_API_KEY" .env 2>/dev/null; then
        if ! grep -q "OPENAI_API_KEY" .env 2>/dev/null; then
            if ! command -v ollama &> /dev/null; then
                echo "Configuration incomplete. Running setup..."
                python3 setup_wizard.py
            fi
        fi
    fi
fi

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

echo ""
echo "========================================"
echo "Starting Streamlit application..."
echo "========================================"
echo ""
echo "Application will open in your browser..."
echo "URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run src/app.py
