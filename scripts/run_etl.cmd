@echo off
REM UNICLOTHES ETL - lanceur sans restriction ExecutionPolicy
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_etl.ps1"
pause
