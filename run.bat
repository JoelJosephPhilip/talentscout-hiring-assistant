@echo off
echo ========================================
echo TalentScout Hiring Assistant
echo ========================================
echo.

REM Check if .env exists with valid configuration
if not exist ".env" (
    echo First-time setup required...
    echo.
    python setup_wizard.py
    if errorlevel 1 (
        echo.
        echo Setup may have failed. Please check the errors above.
        pause
        exit /b 1
    )
) else (
    REM Check if any API key or Ollama is configured
    findstr /C:"GROQ_API_KEY" .env >nul 2>&1
    if errorlevel 1 (
        findstr /C:"OPENAI_API_KEY" .env >nul 2>&1
        if errorlevel 1 (
            ollama list >nul 2>&1
            if errorlevel 1 (
                echo Configuration incomplete. Running setup...
                python setup_wizard.py
            )
        )
    )
)

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Streamlit application...
echo ========================================
echo.
echo Application will open in your browser...
echo URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run src/app.py

pause
