@echo off
REM Windows本地部署脚本
REM Windows Local Deployment Script

echo ========================================
echo 知识管理平台 - Windows本地部署
echo Knowledge Management Platform - Windows Local Deployment
echo ========================================

REM 检查Python版本
echo 检查Python版本... / Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.9+ / Error: Python not found, please install Python 3.9+
    pause
    exit /b 1
)

REM 检查Node.js版本
echo 检查Node.js版本... / Checking Node.js version...
node --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+ / Error: Node.js not found, please install Node.js 16+
    pause
    exit /b 1
)

REM 创建项目目录
echo 创建项目目录... / Creating project directory...
if not exist "knowledge-platform" mkdir knowledge-platform
cd knowledge-platform

REM 后端部署
echo ========================================
echo 部署后端服务... / Deploying backend service...
echo ========================================

cd backend

REM 创建虚拟环境
echo 创建Python虚拟环境... / Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM 安装后端依赖
echo 安装后端依赖... / Installing backend dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM 创建环境配置文件
echo 创建环境配置文件... / Creating environment configuration file...
if not exist ".env" (
    copy .env.example .env
    echo 请编辑 .env 文件配置数据库等信息 / Please edit .env file to configure database and other settings
)

REM 初始化数据库
echo 初始化数据库... / Initializing database...
python -c "from app.core.database_init import create_tables; create_tables()"
python -m alembic upgrade head

REM 创建启动脚本
echo 创建后端启动脚本... / Creating backend startup script...
echo @echo off > start_backend.bat
echo call venv\Scripts\activate.bat >> start_backend.bat
echo uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload >> start_backend.bat

cd ..

REM 前端部署
echo ========================================
echo 部署前端服务... / Deploying frontend service...
echo ========================================

cd frontend

REM 安装前端依赖
echo 安装前端依赖... / Installing frontend dependencies...
npm install

REM 创建环境配置文件
echo 创建前端环境配置... / Creating frontend environment configuration...
echo REACT_APP_API_URL=http://localhost:8000 > .env.local
echo REACT_APP_WS_URL=ws://localhost:8000 >> .env.local

REM 创建启动脚本
echo 创建前端启动脚本... / Creating frontend startup script...
echo @echo off > start_frontend.bat
echo npm start >> start_frontend.bat

REM 创建构建脚本
echo 创建前端构建脚本... / Creating frontend build script...
echo @echo off > build_frontend.bat
echo npm run build >> build_frontend.bat

cd ..

REM 创建总启动脚本
echo 创建总启动脚本... / Creating main startup script...
echo @echo off > start_all.bat
echo echo 启动知识管理平台... / Starting Knowledge Management Platform... >> start_all.bat
echo echo. >> start_all.bat
echo start "后端服务 / Backend Service" cmd /k "cd backend && start_backend.bat" >> start_all.bat
echo timeout /t 5 >> start_all.bat
echo start "前端服务 / Frontend Service" cmd /k "cd frontend && start_frontend.bat" >> start_all.bat
echo echo. >> start_all.bat
echo echo 服务启动完成! / Services started! >> start_all.bat
echo echo 后端服务: http://localhost:8000 / Backend: http://localhost:8000 >> start_all.bat
echo echo 前端服务: http://localhost:3000 / Frontend: http://localhost:3000 >> start_all.bat
echo echo API文档: http://localhost:8000/docs / API Docs: http://localhost:8000/docs >> start_all.bat

REM 创建停止脚本
echo 创建停止脚本... / Creating stop script...
echo @echo off > stop_all.bat
echo echo 停止知识管理平台服务... / Stopping Knowledge Management Platform services... >> stop_all.bat
echo taskkill /f /im python.exe 2^>nul >> stop_all.bat
echo taskkill /f /im node.exe 2^>nul >> stop_all.bat
echo echo 服务已停止 / Services stopped >> stop_all.bat

REM 创建测试脚本
echo 创建测试脚本... / Creating test script...
echo @echo off > run_tests.bat
echo echo 运行测试... / Running tests... >> run_tests.bat
echo cd backend >> run_tests.bat
echo call venv\Scripts\activate.bat >> run_tests.bat
echo python -m pytest tests/ -v >> run_tests.bat
echo cd .. >> run_tests.bat

echo ========================================
echo 部署完成! / Deployment completed!
echo ========================================
echo.
echo 使用方法 / Usage:
echo 1. 启动所有服务 / Start all services: start_all.bat
echo 2. 停止所有服务 / Stop all services: stop_all.bat
echo 3. 运行测试 / Run tests: run_tests.bat
echo.
echo 服务地址 / Service URLs:
echo - 后端API / Backend API: http://localhost:8000
echo - 前端界面 / Frontend UI: http://localhost:3000
echo - API文档 / API Documentation: http://localhost:8000/docs
echo - WebSocket测试 / WebSocket Test: http://localhost:8000/websocket_test.html
echo.
echo 注意事项 / Notes:
echo 1. 请确保端口8000和3000未被占用 / Ensure ports 8000 and 3000 are available
echo 2. 首次运行前请编辑 backend/.env 文件 / Edit backend/.env file before first run
echo 3. 如需生产部署，请使用Docker或Kubernetes / Use Docker or Kubernetes for production
echo.

pause