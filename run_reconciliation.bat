@echo off
echo ========================================
echo  Bank Reconciliation System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Run the main script
echo.
echo Starting reconciliation...
echo ========================================
python main.py

echo.
echo ========================================
echo Reconciliation complete!
echo Check the data\output folder for your report.
echo.
pause