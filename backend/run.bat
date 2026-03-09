@echo off
cd /d "%~dp0"
echo Starting PDS Calc API server...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
