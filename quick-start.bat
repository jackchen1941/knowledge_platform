@echo off
echo ========================================
echo Knowledge Management Platform
echo Windows Quick Start Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo Python and Node.js found. Starting deployment...
echo.

REM Backend setup
echo Setting up backend...
cd backend

REM Create virtual environment
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    echo Creating environment configuration...
    copy .env.example .env
)

REM Initialize database
echo Initializing database...
python -c "from app.core.database_init import init_database; init_database()"

REM Start backend in background
echo Starting backend server...
start "Backend Server" cmd /k "venv\Scripts\activate.bat && python app/main_auto.py"

cd ..

REM Frontend setup
echo Setting up frontend...
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

REM Start frontend
echo Starting frontend server...
start "Frontend Server" cmd /k "npm start"

cd ..

echo.
echo ========================================
echo Deployment completed!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Default admin account: admin / admin123
echo.
echo Press any key to exit...
pause >nul