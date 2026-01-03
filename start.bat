@echo off
SETLOCAL EnableDelayedExpansion

echo Running Alembic Migrations...
alembic upgrade head
IF %ERRORLEVEL% NEQ 0 (
    echo Migration failed. Please check your PostgreSQL connection and .env file.
    pause
    exit /b
)

set /p CHOICE="Do you want to run the database seeder? (y/n): "
IF /I "%CHOICE%"=="y" (
    echo Running Faker seed script...
    python seed_db.py
)

echo Starting Main Application...
streamlit run main.py

pause
