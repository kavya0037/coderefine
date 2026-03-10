@echo off
echo Starting Smart Code Analyser...
start http://localhost:8000
python -m uvicorn main:app --reload --port 8000
pause
