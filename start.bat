@echo off
SETLOCAL EnableDelayedExpansion

IF EXIST venv\Scripts\activate.bat (
    echo Activating Virtual Environment...
    call venv\Scripts\activate.bat
) ELSE (
    echo Error: Virtual environment 'venv' not found.
    pause
    exit /b
)

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
python main.py

pause
