@echo off
REM Run the full CFIC test suite using virtual environment
echo Running CFIC test suite...
.venv\Scripts\python.exe -m pytest -v
