@echo off
echo ========================================
echo TalentScout Hiring Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo ========================================
echo Starting Streamlit application...
echo ========================================
echo.

streamlit run src/app.py

pause
