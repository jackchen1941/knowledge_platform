#!/bin/bash

# 知识管理平台 - 一键启动脚本
# Knowledge Management Platform - Quick Start Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示Logo
show_logo() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║    🚀 知识管理平台 / Knowledge Management Platform           ║"
    echo "║                                                              ║"
    echo "║    ✨ 一键启动 / Quick Start                                 ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 检查系统要求
check_requirements() {
    log_step "检查系统要求... / Checking system requirements..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="Windows"
    else
        log_error "不支持的操作系统: $OSTYPE / Unsupported OS: $OSTYPE"
        exit 1
    fi
    
    log_info "操作系统: $OS / Operating System: $OS"
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker已安装: $DOCKER_VERSION / Docker installed: $DOCKER_VERSION"
    else
        log_error "Docker未安装，请先安装Docker / Docker not installed, please install Docker first"
        echo "安装指南 / Installation guide: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker Compose已安装: $COMPOSE_VERSION / Docker Compose installed: $COMPOSE_VERSION"
    else
        log_error "Docker Compose未安装 / Docker Compose not installed"
        echo "安装指南 / Installation guide: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # 检查端口占用
    check_port() {
        local port=$1
        local service=$2
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warning "端口 $port 被占用 ($service) / Port $port is in use ($service)"
            return 1
        else
            log_info "端口 $port 可用 ($service) / Port $port is available ($service)"
            return 0
        fi
    }
    
    log_step "检查端口占用... / Checking port usage..."
    PORTS_OK=true
    
    check_port 80 "Nginx" || PORTS_OK=false
    check_port 3000 "Frontend" || PORTS_OK=false
    check_port 8000 "Backend" || PORTS_OK=false
    check_port 3306 "MySQL" || PORTS_OK=false
    check_port 6379 "Redis" || PORTS_OK=false
    
    if [ "$PORTS_OK" = false ]; then
        log_warning "部分端口被占用，可能会导致服务冲突 / Some ports are in use, may cause service conflicts"
        read -p "是否继续? (y/N) / Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "用户取消部署 / User cancelled deployment"
            exit 0
        fi
    fi
}

# 选择部署模式
select_deployment_mode() {
    log_step "选择部署模式... / Select deployment mode..."
    
    echo -e "${CYAN}请选择部署模式 / Please select deployment mode:${NC}"
    echo "1) 🚀 完全自动化 (推荐) / Fully Automated (Recommended)"
    echo "2) 🐬 MySQL数据库 / MySQL Database"
    echo "3) 🗄️  SQLite数据库 / SQLite Database"
    echo "4) 🍃 MongoDB数据库 / MongoDB Database"
    echo "5) 📊 包含监控系统 / With Monitoring System"
    
    read -p "请输入选择 (1-5) / Enter choice (1-5): " choice
    
    case $choice in
        1)
            DEPLOYMENT_MODE="auto"
            COMPOSE_FILE="deployment/docker-compose.auto.yml"
            log_info "选择: 完全自动化部署 / Selected: Fully Automated Deployment"
            ;;
        2)
            DEPLOYMENT_MODE="mysql"
            COMPOSE_FILE="deployment/docker-compose.mysql.yml"
            log_info "选择: MySQL数据库部署 / Selected: MySQL Database Deployment"
            ;;
        3)
            DEPLOYMENT_MODE="sqlite"
            COMPOSE_FILE="deployment/docker-compose.sqlite.yml"
            log_info "选择: SQLite数据库部署 / Selected: SQLite Database Deployment"
            ;;
        4)
            DEPLOYMENT_MODE="mongodb"
            COMPOSE_FILE="deployment/docker-compose.mongodb.yml"
            log_info "选择: MongoDB数据库部署 / Selected: MongoDB Database Deployment"
            ;;
        5)
            DEPLOYMENT_MODE="monitoring"
            COMPOSE_FILE="deployment/docker-compose.auto.yml"
            ENABLE_MONITORING=true
            log_info "选择: 包含监控系统 / Selected: With Monitoring System"
            ;;
        *)
            log_warning "无效选择，使用默认模式 / Invalid choice, using default mode"
            DEPLOYMENT_MODE="auto"
            COMPOSE_FILE="deployment/docker-compose.auto.yml"
            ;;
    esac
}

# 准备部署环境
prepare_environment() {
    log_step "准备部署环境... / Preparing deployment environment..."
    
    # 创建必要目录
    mkdir -p deployment/mysql deployment/redis deployment/nginx
    mkdir -p backend/data backend/logs backend/uploads
    mkdir -p monitoring/prometheus monitoring/grafana/dashboards monitoring/grafana/datasources
    
    # 检查配置文件
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "配置文件不存在: $COMPOSE_FILE / Configuration file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    log_success "部署环境准备完成 / Deployment environment prepared"
}

# 构建和启动服务
start_services() {
    log_step "构建和启动服务... / Building and starting services..."
    
    # 拉取最新镜像
    log_info "拉取Docker镜像... / Pulling Docker images..."
    docker-compose -f $COMPOSE_FILE pull
    
    # 构建自定义镜像
    log_info "构建应用镜像... / Building application images..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # 启动服务
    log_info "启动服务... / Starting services..."
    docker-compose -f $COMPOSE_FILE up -d
    
    log_success "服务启动完成 / Services started successfully"
}

# 等待服务就绪
wait_for_services() {
    log_step "等待服务就绪... / Waiting for services to be ready..."
    
    # 等待后端服务
    log_info "等待后端服务启动... / Waiting for backend service..."
    for i in {1..60}; do
        if curl -f http://localhost:8000/status >/dev/null 2>&1; then
            log_success "后端服务已就绪 / Backend service is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            log_error "后端服务启动超时 / Backend service startup timeout"
            show_logs
            exit 1
        fi
        echo -n "."
        sleep 2
    done
    
    # 等待前端服务
    log_info "等待前端服务启动... / Waiting for frontend service..."
    for i in {1..30}; do
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            log_success "前端服务已就绪 / Frontend service is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "前端服务启动超时 / Frontend service startup timeout"
            show_logs
            exit 1
        fi
        echo -n "."
        sleep 2
    done
    
    # 等待Nginx代理
    if [ "$DEPLOYMENT_MODE" = "auto" ] || [ "$ENABLE_MONITORING" = true ]; then
        log_info "等待Nginx代理启动... / Waiting for Nginx proxy..."
        for i in {1..20}; do
            if curl -f http://localhost/status >/dev/null 2>&1; then
                log_success "Nginx代理已就绪 / Nginx proxy is ready"
                break
            fi
            if [ $i -eq 20 ]; then
                log_warning "Nginx代理启动可能有问题 / Nginx proxy may have issues"
            fi
            echo -n "."
            sleep 1
        done
    fi
}

# 显示服务日志
show_logs() {
    log_info "显示服务日志... / Showing service logs..."
    docker-compose -f $COMPOSE_FILE logs --tail=50
}

# 运行健康检查
run_health_check() {
    log_step "运行健康检查... / Running health check..."
    
    # 检查后端健康状态
    if curl -f http://localhost:8000/status >/dev/null 2>&1; then
        BACKEND_STATUS=$(curl -s http://localhost:8000/status | jq -r '.status' 2>/dev/null || echo "unknown")
        log_success "后端状态: $BACKEND_STATUS / Backend status: $BACKEND_STATUS"
    else
        log_error "后端健康检查失败 / Backend health check failed"
        return 1
    fi
    
    # 检查数据库连接
    DB_STATUS=$(curl -s http://localhost:8000/status | jq -r '.database.status' 2>/dev/null || echo "unknown")
    if [ "$DB_STATUS" = "connected" ]; then
        log_success "数据库连接正常 / Database connection normal"
    else
        log_warning "数据库连接状态: $DB_STATUS / Database connection status: $DB_STATUS"
    fi
    
    # 检查Redis连接
    REDIS_STATUS=$(curl -s http://localhost:8000/status | jq -r '.redis.status' 2>/dev/null || echo "unknown")
    if [ "$REDIS_STATUS" = "connected" ]; then
        log_success "Redis连接正常 / Redis connection normal"
    else
        log_info "Redis状态: $REDIS_STATUS / Redis status: $REDIS_STATUS"
    fi
    
    return 0
}

# 显示访问信息
show_access_info() {
    log_step "显示访问信息... / Showing access information..."
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 部署成功! / Deployment Success!        ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║                                                              ║"
    echo "║  📱 前端应用 / Frontend App:                                 ║"
    echo "║     http://localhost:3000                                    ║"
    if [ "$DEPLOYMENT_MODE" = "auto" ] || [ "$ENABLE_MONITORING" = true ]; then
    echo "║     http://localhost (通过Nginx / via Nginx)                 ║"
    fi
    echo "║                                                              ║"
    echo "║  🔧 后端API / Backend API:                                   ║"
    echo "║     http://localhost:8000                                    ║"
    echo "║     http://localhost:8000/docs (API文档 / API Docs)          ║"
    echo "║                                                              ║"
    if [ "$DEPLOYMENT_MODE" = "auto" ] || [ "$DEPLOYMENT_MODE" = "mysql" ]; then
    echo "║  🗄️  数据库管理 / Database Management:                       ║"
    echo "║     http://localhost:8080 (phpMyAdmin)                      ║"
    echo "║     用户名/Username: root                                    ║"
    echo "║     密码/Password: auto_root_password_123                    ║"
    echo "║                                                              ║"
    fi
    if [ "$DEPLOYMENT_MODE" = "auto" ] || [ "$ENABLE_MONITORING" = true ]; then
    echo "║  📊 监控系统 / Monitoring System:                            ║"
    echo "║     http://localhost:3001 (Grafana)                         ║"
    echo "║     用户名/Username: admin                                   ║"
    echo "║     密码/Password: admin123                                  ║"
    echo "║                                                              ║"
    echo "║     http://localhost:9090 (Prometheus)                      ║"
    echo "║                                                              ║"
    echo "║  🔗 Redis管理 / Redis Management:                            ║"
    echo "║     http://localhost:8081 (Redis Commander)                 ║"
    echo "║                                                              ║"
    fi
    echo "║  📋 默认管理员账户 / Default Admin Account:                  ║"
    echo "║     用户名/Username: admin                                   ║"
    echo "║     密码/Password: admin123                                  ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}管理命令 / Management Commands:${NC}"
    echo "  查看日志 / View logs:        docker-compose -f $COMPOSE_FILE logs -f"
    echo "  停止服务 / Stop services:    docker-compose -f $COMPOSE_FILE down"
    echo "  重启服务 / Restart services: docker-compose -f $COMPOSE_FILE restart"
    echo "  查看状态 / Check status:     docker-compose -f $COMPOSE_FILE ps"
    echo ""
}

# 创建管理脚本
create_management_scripts() {
    log_step "创建管理脚本... / Creating management scripts..."
    
    # 创建停止脚本
    cat > stop.sh << EOF
#!/bin/bash
echo "🛑 停止知识管理平台... / Stopping Knowledge Management Platform..."
docker-compose -f $COMPOSE_FILE down
echo "✅ 服务已停止 / Services stopped"
EOF
    chmod +x stop.sh
    
    # 创建重启脚本
    cat > restart.sh << EOF
#!/bin/bash
echo "🔄 重启知识管理平台... / Restarting Knowledge Management Platform..."
docker-compose -f $COMPOSE_FILE restart
echo "✅ 服务已重启 / Services restarted"
EOF
    chmod +x restart.sh
    
    # 创建日志查看脚本
    cat > logs.sh << EOF
#!/bin/bash
echo "📋 查看服务日志... / Viewing service logs..."
docker-compose -f $COMPOSE_FILE logs -f
EOF
    chmod +x logs.sh
    
    # 创建状态检查脚本
    cat > status.sh << EOF
#!/bin/bash
echo "📊 检查服务状态... / Checking service status..."
docker-compose -f $COMPOSE_FILE ps
echo ""
echo "🔍 健康检查... / Health check..."
curl -s http://localhost:8000/status | jq . 2>/dev/null || curl -s http://localhost:8000/status
EOF
    chmod +x status.sh
    
    log_success "管理脚本创建完成 / Management scripts created"
}

# 主函数
main() {
    show_logo
    
    # 检查是否以root权限运行
    if [ "$EUID" -eq 0 ]; then
        log_warning "不建议以root权限运行 / Not recommended to run as root"
    fi
    
    # 执行部署步骤
    check_requirements
    select_deployment_mode
    prepare_environment
    start_services
    wait_for_services
    
    # 运行健康检查
    if run_health_check; then
        show_access_info
        create_management_scripts
        
        log_success "🎉 知识管理平台部署完成! / Knowledge Management Platform deployment completed!"
        log_info "💡 提示: 首次启动可能需要几分钟来初始化数据库 / Tip: First startup may take a few minutes to initialize database"
    else
        log_error "健康检查失败，请查看日志 / Health check failed, please check logs"
        show_logs
        exit 1
    fi
}

# 错误处理
trap 'log_error "部署过程中发生错误 / Error occurred during deployment"; exit 1' ERR

# 运行主函数
main "$@"