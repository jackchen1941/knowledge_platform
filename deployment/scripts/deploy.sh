#!/bin/bash

# 知识管理平台部署脚本
# Knowledge Management Platform Deployment Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 显示帮助信息
show_help() {
    echo "知识管理平台部署脚本 / Knowledge Management Platform Deployment Script"
    echo ""
    echo "用法 / Usage:"
    echo "  $0 [选项] [部署类型] / $0 [options] [deployment-type]"
    echo ""
    echo "部署类型 / Deployment Types:"
    echo "  local       本地部署 (SQLite) / Local deployment (SQLite)"
    echo "  docker      Docker部署 / Docker deployment"
    echo "  k8s         Kubernetes部署 / Kubernetes deployment"
    echo "  helm        Helm Chart部署 / Helm Chart deployment"
    echo ""
    echo "选项 / Options:"
    echo "  -d, --database    数据库类型 (sqlite|mysql|postgresql|mongodb) / Database type"
    echo "  -e, --env         环境 (development|production) / Environment"
    echo "  -h, --help        显示帮助信息 / Show help"
    echo "  -v, --verbose     详细输出 / Verbose output"
    echo ""
    echo "示例 / Examples:"
    echo "  $0 local                           # 本地部署，使用SQLite"
    echo "  $0 docker -d mysql                # Docker部署，使用MySQL"
    echo "  $0 k8s -d postgresql -e production # K8s部署，使用PostgreSQL"
    echo "  $0 helm -d mysql -e production     # Helm部署，使用MySQL"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖... / Checking system dependencies..."
    
    case $DEPLOYMENT_TYPE in
        "local")
            command -v python3 >/dev/null 2>&1 || { log_error "Python 3.9+ 未安装 / Python 3.9+ not installed"; exit 1; }
            command -v node >/dev/null 2>&1 || { log_error "Node.js 16+ 未安装 / Node.js 16+ not installed"; exit 1; }
            ;;
        "docker")
            command -v docker >/dev/null 2>&1 || { log_error "Docker 未安装 / Docker not installed"; exit 1; }
            command -v docker-compose >/dev/null 2>&1 || { log_error "Docker Compose 未安装 / Docker Compose not installed"; exit 1; }
            ;;
        "k8s")
            command -v kubectl >/dev/null 2>&1 || { log_error "kubectl 未安装 / kubectl not installed"; exit 1; }
            ;;
        "helm")
            command -v helm >/dev/null 2>&1 || { log_error "Helm 未安装 / Helm not installed"; exit 1; }
            command -v kubectl >/dev/null 2>&1 || { log_error "kubectl 未安装 / kubectl not installed"; exit 1; }
            ;;
    esac
    
    log_success "依赖检查完成 / Dependencies check completed"
}

# 本地部署
deploy_local() {
    log_info "开始本地部署... / Starting local deployment..."
    
    # 后端部署
    log_info "部署后端服务... / Deploying backend service..."
    cd backend
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # 安装依赖
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 创建环境文件
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log_warning "请编辑 .env 文件配置数据库等信息 / Please edit .env file to configure database settings"
    fi
    
    # 初始化数据库
    python -c "from app.core.database_init import create_tables; create_tables()"
    alembic upgrade head
    
    cd ..
    
    # 前端部署
    log_info "部署前端服务... / Deploying frontend service..."
    cd frontend
    
    # 安装依赖
    npm install
    
    # 创建环境文件
    cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
EOF
    
    cd ..
    
    # 创建启动脚本
    cat > start.sh << 'EOF'
#!/bin/bash
echo "启动知识管理平台... / Starting Knowledge Management Platform..."

# 启动后端
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 5

# 启动前端
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "服务启动完成! / Services started!"
echo "后端服务 / Backend: http://localhost:8000"
echo "前端服务 / Frontend: http://localhost:3000"
echo "API文档 / API Docs: http://localhost:8000/docs"

# 等待用户输入停止服务
echo "按 Ctrl+C 停止服务 / Press Ctrl+C to stop services"
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    
    chmod +x start.sh
    
    log_success "本地部署完成! / Local deployment completed!"
    log_info "运行 ./start.sh 启动服务 / Run ./start.sh to start services"
}

# Docker部署
deploy_docker() {
    log_info "开始Docker部署... / Starting Docker deployment..."
    
    # 选择docker-compose文件
    case $DATABASE_TYPE in
        "sqlite")
            COMPOSE_FILE="deployment/docker-compose.sqlite.yml"
            ;;
        "mysql")
            COMPOSE_FILE="deployment/docker-compose.mysql.yml"
            ;;
        "mongodb")
            COMPOSE_FILE="deployment/docker-compose.mongodb.yml"
            ;;
        *)
            COMPOSE_FILE="deployment/docker-compose.mysql.yml"
            ;;
    esac
    
    log_info "使用配置文件: $COMPOSE_FILE / Using configuration file: $COMPOSE_FILE"
    
    # 构建并启动服务
    docker-compose -f $COMPOSE_FILE up -d --build
    
    # 等待服务启动
    log_info "等待服务启动... / Waiting for services to start..."
    sleep 30
    
    # 检查服务状态
    docker-compose -f $COMPOSE_FILE ps
    
    log_success "Docker部署完成! / Docker deployment completed!"
    log_info "服务地址 / Service URLs:"
    log_info "- 前端 / Frontend: http://localhost:3000"
    log_info "- 后端API / Backend API: http://localhost:8000"
    log_info "- API文档 / API Docs: http://localhost:8000/docs"
}

# Kubernetes部署
deploy_k8s() {
    log_info "开始Kubernetes部署... / Starting Kubernetes deployment..."
    
    # 创建命名空间
    kubectl apply -f deployment/kubernetes/namespace.yaml
    
    # 应用配置
    kubectl apply -f deployment/kubernetes/configmap.yaml
    kubectl apply -f deployment/kubernetes/secrets.yaml
    
    # 部署数据库
    case $DATABASE_TYPE in
        "mysql")
            kubectl apply -f deployment/kubernetes/mysql-deployment.yaml
            ;;
        "postgresql")
            # 这里可以添加PostgreSQL部署配置
            log_warning "PostgreSQL配置需要单独创建 / PostgreSQL configuration needs to be created separately"
            ;;
    esac
    
    # 部署Redis
    kubectl apply -f deployment/kubernetes/redis-deployment.yaml
    
    # 部署应用服务
    kubectl apply -f deployment/kubernetes/backend-deployment.yaml
    kubectl apply -f deployment/kubernetes/frontend-deployment.yaml
    
    # 配置Ingress
    kubectl apply -f deployment/kubernetes/ingress.yaml
    
    # 等待部署完成
    log_info "等待部署完成... / Waiting for deployment to complete..."
    kubectl wait --for=condition=available --timeout=300s deployment/backend -n knowledge-platform
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n knowledge-platform
    
    # 显示部署状态
    kubectl get pods -n knowledge-platform
    kubectl get services -n knowledge-platform
    
    log_success "Kubernetes部署完成! / Kubernetes deployment completed!"
    log_info "使用以下命令查看服务状态 / Use following commands to check service status:"
    log_info "kubectl get pods -n knowledge-platform"
    log_info "kubectl get services -n knowledge-platform"
}

# Helm部署
deploy_helm() {
    log_info "开始Helm部署... / Starting Helm deployment..."
    
    # 创建命名空间
    kubectl create namespace knowledge-platform --dry-run=client -o yaml | kubectl apply -f -
    
    # 根据数据库类型设置values
    VALUES_FILE="deployment/helm-chart/values-${DATABASE_TYPE}.yaml"
    if [ ! -f "$VALUES_FILE" ]; then
        VALUES_FILE="deployment/helm-chart/values.yaml"
    fi
    
    # 安装或升级Helm Chart
    helm upgrade --install knowledge-platform deployment/helm-chart \
        --namespace knowledge-platform \
        --values $VALUES_FILE \
        --set database.type=$DATABASE_TYPE \
        --set config.environment=$ENVIRONMENT \
        --wait --timeout=600s
    
    # 显示部署状态
    helm status knowledge-platform -n knowledge-platform
    kubectl get pods -n knowledge-platform
    
    log_success "Helm部署完成! / Helm deployment completed!"
    log_info "使用以下命令查看状态 / Use following commands to check status:"
    log_info "helm status knowledge-platform -n knowledge-platform"
    log_info "kubectl get pods -n knowledge-platform"
}

# 运行测试
run_tests() {
    log_info "运行测试... / Running tests..."
    
    case $DEPLOYMENT_TYPE in
        "local")
            cd backend
            source venv/bin/activate
            python -m pytest tests/ -v
            cd ..
            ;;
        "docker")
            docker-compose -f $COMPOSE_FILE exec backend python -m pytest tests/ -v
            ;;
        "k8s"|"helm")
            kubectl exec -it deployment/backend -n knowledge-platform -- python -m pytest tests/ -v
            ;;
    esac
    
    log_success "测试完成 / Tests completed"
}

# 主函数
main() {
    # 默认值
    DEPLOYMENT_TYPE=""
    DATABASE_TYPE="sqlite"
    ENVIRONMENT="development"
    VERBOSE=false
    RUN_TESTS=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--database)
                DATABASE_TYPE="$2"
                shift 2
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -t|--test)
                RUN_TESTS=true
                shift
                ;;
            local|docker|k8s|helm)
                DEPLOYMENT_TYPE="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1 / Unknown parameter: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查部署类型
    if [ -z "$DEPLOYMENT_TYPE" ]; then
        log_error "请指定部署类型 / Please specify deployment type"
        show_help
        exit 1
    fi
    
    # 显示配置信息
    log_info "部署配置 / Deployment Configuration:"
    log_info "- 部署类型 / Deployment Type: $DEPLOYMENT_TYPE"
    log_info "- 数据库类型 / Database Type: $DATABASE_TYPE"
    log_info "- 环境 / Environment: $ENVIRONMENT"
    
    # 检查依赖
    check_dependencies
    
    # 执行部署
    case $DEPLOYMENT_TYPE in
        "local")
            deploy_local
            ;;
        "docker")
            deploy_docker
            ;;
        "k8s")
            deploy_k8s
            ;;
        "helm")
            deploy_helm
            ;;
    esac
    
    # 运行测试
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    log_success "部署完成! / Deployment completed!"
}

# 运行主函数
main "$@"