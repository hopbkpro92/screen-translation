@echo off
REM Run the Screen Translation application

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the application
python main.py

pause
