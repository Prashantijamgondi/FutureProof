@echo off
echo ========================================
echo FutureProof Backend Setup (Windows)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11+
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not found. Please install Docker Desktop
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [4/6] Copying environment file...
if not exist .env (
    copy .env.example .env
    echo CREATED: .env file. Please update with your API keys!
) else (
    echo .env already exists
)

echo [5/6] Setting up database...
docker-compose up -d postgres redis

echo Waiting for database to be ready...
timeout /t 10 /nobreak >nul

echo [6/6] Running database migrations...
alembic upgrade head

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Run: docker-compose up
echo 3. Visit: http://localhost:8000/docs
echo.
echo To activate venv: venv\Scripts\activate.bat
echo ========================================
