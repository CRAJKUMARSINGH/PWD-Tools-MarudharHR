@echo off
echo Starting MarudharHR Receipt Generator...
echo.

REM Kill any existing Python processes running the app
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

REM Start the Flask application
echo Starting Flask application...
python app.py

pause
