@echo off
title HydraMetric Launcher
echo Starting HydraMetric AI Backend...

:: Start the Python backend using the virtual environment in a new window
start "HydraMetric AI Server" cmd /k ".\venv\Scripts\python.exe backend\app.py"

:: Wait 3 seconds for the server to load the AI model
echo Waiting for YOLOv26 AI Model to load...
timeout /t 4 /nobreak >nul

:: Open the dashboard in the default web browser (using the server URL to avoid CORS issues)
echo Opening Dashboard...
start "" "http://localhost:5000/"

exit
