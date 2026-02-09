# 知识管理平台 - 部署指南
# Knowledge Management Platform - Deployment Guide

## 📋 目录 / Table of Contents

1. [快速开始 / Quick Start](#快速开始--quick-start)
2. [部署方式对比 / Deployment Comparison](#部署方式对比--deployment-comparison)
3. [Windows本地部署 / Windows Local Deployment](#windows本地部署--windows-local-deployment)
4. [Linux/macOS本地部署 / Linux/macOS Local Deployment](#linuxmacos本地部署--linuxmacos-local-deployment)
5. [Docker部署 / Docker Deployment](#docker部署--docker-deployment)
6. [Kubernetes部署 / Kubernetes Deployment](#kubernetes部署--kubernetes-deployment)
7. [Helm Chart部署 / Helm Chart Deployment](#helm-chart部署--helm-chart-deployment)
8. [数据库配置 / Database Configuration](#数据库配置--database-configuration)
9. [监控与维护 / Monitoring & Maintenance](#监控与维护--monitoring--maintenance)
10. [故障排除 / Troubleshooting](#故障排除--troubleshooting)

---

## 快速开始 / Quick Start

### 🚀 一键部署 / One-Click Deployment

**Windows用户 / Windows Users:**
```batch
# 下载并运行安装脚本
curl -O https://raw.githubusercontent.com/knowledge-platform/deployment/main/windows/install.bat
install.bat
```

**Linux/macOS用户 / Linux/macOS Users:**
```bash
# 下载并运行部署脚本
curl -O https://raw.githubusercontent.com/knowledge-platform/deployment/main/scripts/deploy.sh
chmod +x deploy.sh

# 本地部署 (SQLite)
./deploy.sh local

# Docker部署 (MySQL)
./deploy.sh docker -d mysql

# Kubernetes部署 (PostgreSQL)
./deploy.sh k8s -d postgresql -e production
```

### 📊 部署选择建议 / Deployment Recommendations

| 场景 / Scenario | 推荐方式 / Recommended | 数据库 / Database | 说明 / Description |
|-----------------|----------------------|------------------|-------------------|
| 个人开发 / Personal Dev | 本地部署 / Local | SQLite | 快速启动，无需额外配置 |
| 团队开发 / Team Dev | Docker | MySQL | 环境一致，易于共享 |
| 测试环境 / Testing | Docker | MySQL/PostgreSQL | 隔离环境，快速重置 |
| 生产环境 / Production | Kubernetes/Helm | PostgreSQL/MySQL | 高可用，自动扩缩容 |
| 企业部署 / Enterprise | Helm Chart | PostgreSQL | 完整监控，企业级特性 |

---

## 部署方式对比 / Deployment Comparison

### 📈 功能对比表 / Feature Comparison

| 特性 / Feature | 本地部署 / Local | Docker | Kubernetes | Helm Chart |
|---------------|-----------------|--------|------------|------------|
| **部署难度 / Complexity** | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐ 复杂 | ⭐⭐⭐⭐ 高级 |
| **资源需求 / Resources** | 低 / Low | 中 / Medium | 高 / High | 高 / High |
| **扩展性 / Scalability** | ❌ 无 | ⚠️ 有限 | ✅ 优秀 | ✅ 优秀 |
| **高可用 / High Availability** | ❌ 无 | ⚠️ 有限 | ✅ 支持 | ✅ 支持 |
| **监控 / Monitoring** | ⚠️ 基础 | ⚠️ 基础 | ✅ 完整 | ✅ 完整 |
| **自动恢复 / Auto Recovery** | ❌ 无 | ⚠️ 有限 | ✅ 支持 | ✅ 支持 |
| **配置管理 / Config Management** | ⚠️ 手动 | ⚠️ 环境变量 | ✅ ConfigMap | ✅ Values |
| **适用场景 / Use Cases** | 开发测试 | 小团队 | 生产环境 | 企业级 |

### 💰 成本对比 / Cost Comparison

| 部署方式 / Method | 硬件成本 / Hardware | 维护成本 / Maintenance | 学习成本 / Learning |
|------------------|-------------------|---------------------|-------------------|
| 本地部署 / Local | 💰 低 | 💰 低 | 💰 低 |
| Docker | 💰💰 中 | 💰💰 中 | 💰💰 中 |
| Kubernetes | 💰💰💰 高 | 💰💰💰 高 | 💰💰💰 高 |
| Helm Chart | 💰💰💰 高 | 💰💰 中 | 💰💰💰💰 很高 |

---

## Windows本地部署 / Windows Local Deployment

### 🖥️ 系统要求 / System Requirements

- **操作系统 / OS**: Windows 10/11
- **Python**: 3.9+ (推荐 3.11)
- **Node.js**: 16+ (推荐 18 LTS)
- **内存 / RAM**: 4GB+ (推荐 8GB)
- **磁盘空间 / Disk**: 2GB+

### 📦 安装步骤 / Installation Steps

**1. 下载安装脚本 / Download Installation Script**
```batch
# 方式1: 直接下载
curl -O https://raw.githubusercontent.com/knowledge-platform/deployment/main/windows/install.bat

# 方式2: 手动创建 (如果curl不可用)
# 复制 deployment/windows/install.bat 内容到本地文件
```

**2. 运行安装脚本 / Run Installation Script**
```batch
# 以管理员身份运行
install.bat
```

**3. 配置环境 / Configure Environment**
```batch
# 编辑后端配置文件
notepad backend\.env

# 主要配置项:
DATABASE_URL=sqlite:///./knowledge_platform.db
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```

**4. 启动服务 / Start Services**
```batch
# 启动所有服务
start_all.bat

# 或分别启动
cd backend && start_backend.bat
cd frontend && start_frontend.bat
```

### 🔧 Windows特定配置 / Windows-Specific Configuration

**PowerShell执行策略 / PowerShell Execution Policy:**
```powershell
# 如果遇到执行策略问题
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**防火墙配置 / Firewall Configuration:**
```batch
# 允许端口8000和3000通过防火墙
netsh advfirewall firewall add rule name="Knowledge Platform Backend" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="Knowledge Platform Frontend" dir=in action=allow protocol=TCP localport=3000
```

**服务管理 / Service Management:**
```batch
# 查看运行的服务
tasklist | findstr python
tasklist | findstr node

# 停止服务
stop_all.bat
```

---

## Linux/macOS本地部署 / Linux/macOS Local Deployment

### 🐧 系统要求 / System Requirements

- **操作系统 / OS**: Ubuntu 20.04+, CentOS 8+, macOS 11+
- **Python**: 3.9+ (推荐 3.11)
- **Node.js**: 16+ (推荐 18 LTS)
- **内存 / RAM**: 4GB+ (推荐 8GB)
- **磁盘空间 / Disk**: 2GB+

### 📦 安装步骤 / Installation Steps

**1. 安装系统依赖 / Install System Dependencies**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm git curl
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip nodejs npm git curl
```

**macOS:**
```bash
# 使用Homebrew
brew install python@3.11 node git
```

**2. 使用部署脚本 / Use Deployment Script**
```bash
# 下载部署脚本
curl -O https://raw.githubusercontent.com/knowledge-platform/deployment/main/scripts/deploy.sh
chmod +x deploy.sh

# 本地部署
./deploy.sh local

# 查看帮助
./deploy.sh --help
```

**3. 手动部署 (可选) / Manual Deployment (Optional)**
```bash
# 克隆项目
git clone <repository-url>
cd knowledge-management-platform

# 后端部署
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件
alembic upgrade head

# 前端部署
cd ../frontend
npm install
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
echo "REACT_APP_WS_URL=ws://localhost:8000" >> .env.local

# 启动服务
cd ../backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
cd ../frontend && npm start &
```

### 🔧 Linux/macOS特定配置 / Linux/macOS-Specific Configuration

**系统服务配置 / System Service Configuration:**
```bash
# 创建systemd服务文件 (Linux)
sudo tee /etc/systemd/system/knowledge-platform-backend.service > /dev/null <<EOF
[Unit]
Description=Knowledge Platform Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/knowledge-platform/backend
Environment=PATH=/path/to/knowledge-platform/backend/venv/bin
ExecStart=/path/to/knowledge-platform/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl enable knowledge-platform-backend
sudo systemctl start knowledge-platform-backend
```

**Nginx反向代理配置 / Nginx Reverse Proxy Configuration:**
```nginx
# /etc/nginx/sites-available/knowledge-platform
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Docker部署 / Docker Deployment

### 🐳 系统要求 / System Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **内存 / RAM**: 8GB+ (推荐 16GB)
- **磁盘空间 / Disk**: 10GB+

### 📦 部署步骤 / Deployment Steps

**1. 安装Docker / Install Docker**

**Ubuntu:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Windows:**
下载并安装 Docker Desktop for Windows

**macOS:**
下载并安装 Docker Desktop for Mac

**2. 选择部署配置 / Choose Deployment Configuration**

**SQLite配置 (开发环境) / SQLite Configuration (Development):**
```bash
# 使用SQLite数据库
docker-compose -f deployment/docker-compose.sqlite.yml up -d
```

**MySQL配置 (生产环境) / MySQL Configuration (Production):**
```bash
# 使用MySQL数据库
docker-compose -f deployment/docker-compose.mysql.yml up -d
```

**MongoDB配置 (文档存储) / MongoDB Configuration (Document Storage):**
```bash
# 使用MongoDB数据库
docker-compose -f deployment/docker-compose.mongodb.yml up -d
```

**3. 使用部署脚本 / Use Deployment Script**
```bash
# 自动选择配置
./deployment/scripts/deploy.sh docker -d mysql -e production
```

### 🔧 Docker配置详解 / Docker Configuration Details

**环境变量配置 / Environment Variables:**
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  backend:
    environment:
      - SECRET_KEY=your-production-secret-key
      - DATABASE_URL=mysql+aiomysql://user:password@mysql:3306/knowledge_platform
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
      - DEBUG=false
```

**数据持久化 / Data Persistence:**
```yaml
volumes:
  mysql_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/mysql/data
  
  redis_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/redis/data
```

**网络配置 / Network Configuration:**
```yaml
networks:
  knowledge-platform:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 📊 Docker管理命令 / Docker Management Commands

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启服务
docker-compose restart backend

# 更新服务
docker-compose pull
docker-compose up -d

# 清理资源
docker-compose down -v
docker system prune -a
```

---

## Kubernetes部署 / Kubernetes Deployment

### ☸️ 系统要求 / System Requirements

- **Kubernetes**: 1.20+
- **kubectl**: 配置并连接到集群
- **内存 / RAM**: 16GB+ (集群总计)
- **CPU**: 8核+ (集群总计)
- **存储 / Storage**: 100GB+ (持久化存储)

### 📦 部署步骤 / Deployment Steps

**1. 准备Kubernetes集群 / Prepare Kubernetes Cluster**

**本地集群 (minikube) / Local Cluster (minikube):**
```bash
# 安装minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 启动集群
minikube start --memory=8192 --cpus=4
minikube addons enable ingress
```

**云服务集群 / Cloud Service Cluster:**
```bash
# AWS EKS
eksctl create cluster --name knowledge-platform --region us-west-2

# Google GKE
gcloud container clusters create knowledge-platform --zone us-central1-a

# Azure AKS
az aks create --resource-group myResourceGroup --name knowledge-platform
```

**2. 部署应用 / Deploy Application**

**使用部署脚本 / Use Deployment Script:**
```bash
./deployment/scripts/deploy.sh k8s -d mysql -e production
```

**手动部署 / Manual Deployment:**
```bash
# 创建命名空间
kubectl apply -f deployment/kubernetes/namespace.yaml

# 应用配置
kubectl apply -f deployment/kubernetes/configmap.yaml
kubectl apply -f deployment/kubernetes/secrets.yaml

# 部署数据库
kubectl apply -f deployment/kubernetes/mysql-deployment.yaml
kubectl apply -f deployment/kubernetes/redis-deployment.yaml

# 部署应用
kubectl apply -f deployment/kubernetes/backend-deployment.yaml
kubectl apply -f deployment/kubernetes/frontend-deployment.yaml

# 配置网络
kubectl apply -f deployment/kubernetes/ingress.yaml
```

**3. 验证部署 / Verify Deployment**
```bash
# 检查Pod状态
kubectl get pods -n knowledge-platform

# 检查服务状态
kubectl get services -n knowledge-platform

# 检查Ingress状态
kubectl get ingress -n knowledge-platform

# 查看日志
kubectl logs -f deployment/backend -n knowledge-platform
```

### 🔧 Kubernetes配置详解 / Kubernetes Configuration Details

**资源限制 / Resource Limits:**
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**健康检查 / Health Checks:**
```yaml
livenessProbe:
  httpGet:
    path: /status
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

**自动扩缩容 / Auto Scaling:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 📊 Kubernetes管理命令 / Kubernetes Management Commands

```bash
# 扩缩容
kubectl scale deployment backend --replicas=5 -n knowledge-platform

# 滚动更新
kubectl set image deployment/backend backend=knowledge-platform/backend:v2.0.0 -n knowledge-platform

# 查看资源使用
kubectl top pods -n knowledge-platform
kubectl top nodes

# 故障排除
kubectl describe pod <pod-name> -n knowledge-platform
kubectl exec -it <pod-name> -n knowledge-platform -- /bin/bash

# 备份配置
kubectl get all -n knowledge-platform -o yaml > backup.yaml
```

---

## Helm Chart部署 / Helm Chart Deployment

### ⚓ 系统要求 / System Requirements

- **Helm**: 3.0+
- **Kubernetes**: 1.20+
- **kubectl**: 配置并连接到集群

### 📦 部署步骤 / Deployment Steps

**1. 安装Helm / Install Helm**
```bash
# Linux/macOS
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Windows (使用Chocolatey)
choco install kubernetes-helm
```

**2. 部署应用 / Deploy Application**

**使用部署脚本 / Use Deployment Script:**
```bash
./deployment/scripts/deploy.sh helm -d mysql -e production
```

**手动部署 / Manual Deployment:**
```bash
# 创建命名空间
kubectl create namespace knowledge-platform

# 安装Chart
helm install knowledge-platform deployment/helm-chart \
  --namespace knowledge-platform \
  --set database.type=mysql \
  --set config.environment=production \
  --wait
```

**3. 自定义配置 / Custom Configuration**

**创建自定义values文件 / Create Custom Values File:**
```yaml
# values-production.yaml
global:
  imageRegistry: "your-registry.com"

backend:
  replicaCount: 5
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

database:
  type: mysql
  mysql:
    auth:
      rootPassword: "your-secure-password"
      database: "knowledge_platform"
      username: "app_user"
      password: "your-app-password"

ingress:
  enabled: true
  hosts:
    - host: knowledge-platform.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: knowledge-platform-tls
      hosts:
        - knowledge-platform.yourdomain.com
```

**使用自定义配置部署 / Deploy with Custom Configuration:**
```bash
helm install knowledge-platform deployment/helm-chart \
  --namespace knowledge-platform \
  --values values-production.yaml \
  --wait
```

### 🔧 Helm管理命令 / Helm Management Commands

```bash
# 查看发布状态
helm status knowledge-platform -n knowledge-platform

# 查看发布历史
helm history knowledge-platform -n knowledge-platform

# 升级发布
helm upgrade knowledge-platform deployment/helm-chart \
  --namespace knowledge-platform \
  --values values-production.yaml

# 回滚发布
helm rollback knowledge-platform 1 -n knowledge-platform

# 卸载发布
helm uninstall knowledge-platform -n knowledge-platform

# 测试发布
helm test knowledge-platform -n knowledge-platform
```

### 📊 Helm Chart结构 / Helm Chart Structure

```
deployment/helm-chart/
├── Chart.yaml              # Chart元数据
├── values.yaml             # 默认配置值
├── templates/              # Kubernetes模板文件
│   ├── deployment.yaml     # 部署配置
│   ├── service.yaml        # 服务配置
│   ├── ingress.yaml        # Ingress配置
│   ├── configmap.yaml      # ConfigMap配置
│   ├── secrets.yaml        # Secrets配置
│   └── hpa.yaml           # 自动扩缩容配置
├── charts/                 # 依赖Chart
└── templates/tests/        # 测试模板
```

---

## 数据库配置 / Database Configuration

### 🗄️ 数据库选择指南 / Database Selection Guide

| 数据库 / Database | 适用场景 / Use Case | 优势 / Advantages | 劣势 / Disadvantages |
|------------------|-------------------|------------------|-------------------|
| **SQLite** | 开发、测试、小型部署 | 零配置、轻量级、快速 | 不支持并发写入、功能有限 |
| **MySQL** | 生产环境、中大型应用 | 成熟稳定、性能好、生态丰富 | 配置复杂、资源消耗较高 |
| **PostgreSQL** | 企业级、复杂查询 | 功能强大、标准兼容、扩展性好 | 学习成本高、配置复杂 |
| **MongoDB** | 文档存储、灵活结构 | 灵活模式、水平扩展、JSON原生 | 事务支持有限、内存消耗大 |

### 📊 SQLite配置 / SQLite Configuration

**适用场景 / Use Cases:**
- 本地开发环境
- 原型验证
- 小型单用户应用
- 测试环境

**配置示例 / Configuration Example:**
```python
# backend/app/core/config.py
DATABASE_URL = "sqlite:///./data/knowledge_platform.db"

# 环境变量
DATABASE_URL=sqlite:///./data/knowledge_platform.db
```

**优化配置 / Optimization:**
```python
# SQLite特定优化
SQLITE_PRAGMAS = {
    'journal_mode': 'WAL',
    'cache_size': -1024 * 64,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0
}
```

### 🐬 MySQL配置 / MySQL Configuration

**适用场景 / Use Cases:**
- 生产环境
- 多用户并发访问
- 中大型应用
- 需要复制和备份

**Docker配置 / Docker Configuration:**
```yaml
mysql:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: rootpassword123
    MYSQL_DATABASE: knowledge_platform
    MYSQL_USER: app_user
    MYSQL_PASSWORD: app_password
  command: >
    --default-authentication-plugin=mysql_native_password
    --character-set-server=utf8mb4
    --collation-server=utf8mb4_unicode_ci
    --innodb-buffer-pool-size=256M
    --max-connections=200
```

**应用配置 / Application Configuration:**
```python
DATABASE_URL = "mysql+aiomysql://app_user:app_password@mysql:3306/knowledge_platform?charset=utf8mb4"

# 连接池配置
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
```

**性能优化 / Performance Optimization:**
```sql
-- MySQL配置优化
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
max_connections = 200
query_cache_size = 64M
tmp_table_size = 64M
max_heap_table_size = 64M
```

### 🐘 PostgreSQL配置 / PostgreSQL Configuration

**适用场景 / Use Cases:**
- 企业级应用
- 复杂查询需求
- 需要高级功能 (JSON、全文搜索等)
- 数据分析场景

**Docker配置 / Docker Configuration:**
```yaml
postgresql:
  image: postgres:14
  environment:
    POSTGRES_DB: knowledge_platform
    POSTGRES_USER: app_user
    POSTGRES_PASSWORD: app_password
    POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
  command: >
    postgres
    -c shared_preload_libraries=pg_stat_statements
    -c pg_stat_statements.track=all
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
```

**应用配置 / Application Configuration:**
```python
DATABASE_URL = "postgresql+asyncpg://app_user:app_password@postgresql:5432/knowledge_platform"

# 连接池配置
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
DATABASE_POOL_TIMEOUT = 30
```

### 🍃 MongoDB配置 / MongoDB Configuration

**适用场景 / Use Cases:**
- 文档存储需求
- 灵活的数据结构
- 大数据场景
- 内容管理系统

**Docker配置 / Docker Configuration:**
```yaml
mongodb:
  image: mongo:6.0
  environment:
    MONGO_INITDB_ROOT_USERNAME: root
    MONGO_INITDB_ROOT_PASSWORD: rootpassword123
    MONGO_INITDB_DATABASE: knowledge_platform
  command: >
    mongod
    --auth
    --bind_ip_all
    --wiredTigerCacheSizeGB 1
    --wiredTigerCollectionBlockCompressor snappy
```

**应用配置 / Application Configuration:**
```python
MONGODB_URL = "mongodb://root:rootpassword123@mongodb:27017/knowledge_platform?authSource=admin"

# MongoDB特定配置
MONGODB_SETTINGS = {
    'maxPoolSize': 50,
    'minPoolSize': 5,
    'maxIdleTimeMS': 30000,
    'serverSelectionTimeoutMS': 5000,
    'socketTimeoutMS': 20000,
    'connectTimeoutMS': 10000
}
```

### 🔄 数据库迁移 / Database Migration

**SQLAlchemy迁移 / SQLAlchemy Migration:**
```bash
# 创建迁移文件
alembic revision --autogenerate -m "Add new feature"

# 应用迁移
alembic upgrade head

# 查看迁移历史
alembic history

# 回滚迁移
alembic downgrade -1
```

**数据备份策略 / Data Backup Strategy:**
```bash
# MySQL备份
mysqldump -u app_user -p knowledge_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# PostgreSQL备份
pg_dump -U app_user -h localhost knowledge_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# MongoDB备份
mongodump --uri="mongodb://root:rootpassword123@mongodb:27017/knowledge_platform" --out=backup_$(date +%Y%m%d_%H%M%S)
```

---

## 监控与维护 / Monitoring & Maintenance

### 📊 监控系统 / Monitoring System

**Prometheus + Grafana配置 / Prometheus + Grafana Configuration:**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  prometheus_data:
  grafana_data:
```

**应用监控指标 / Application Metrics:**
```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 请求计数器
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])

# 请求延迟
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# 活跃连接数
ACTIVE_CONNECTIONS = Gauge('websocket_connections_active', 'Active WebSocket connections')

# 数据库连接池
DB_POOL_SIZE = Gauge('database_pool_size', 'Database connection pool size')
```

### 📋 日志管理 / Log Management

**结构化日志配置 / Structured Logging Configuration:**
```python
# backend/app/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

**ELK Stack集成 / ELK Stack Integration:**
```yaml
# docker-compose.elk.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./elk/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

### 🔧 维护任务 / Maintenance Tasks

**自动化维护脚本 / Automated Maintenance Script:**
```bash
#!/bin/bash
# maintenance.sh

echo "开始系统维护... / Starting system maintenance..."

# 数据库优化
echo "优化数据库... / Optimizing database..."
docker-compose exec mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "
    ANALYZE TABLE knowledge_items;
    OPTIMIZE TABLE knowledge_items;
    ANALYZE TABLE users;
    OPTIMIZE TABLE users;
"

# 清理日志文件
echo "清理日志文件... / Cleaning log files..."
find ./logs -name "*.log" -mtime +30 -delete
find ./logs -name "*.log.*" -mtime +7 -delete

# 清理临时文件
echo "清理临时文件... / Cleaning temporary files..."
docker system prune -f
docker volume prune -f

# 备份数据库
echo "备份数据库... / Backing up database..."
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD knowledge_platform > backups/$BACKUP_FILE

# 检查磁盘空间
echo "检查磁盘空间... / Checking disk space..."
df -h

echo "维护完成 / Maintenance completed"
```

**定时任务配置 / Cron Job Configuration:**
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点执行维护任务
0 2 * * * /path/to/maintenance.sh >> /var/log/maintenance.log 2>&1

# 每小时检查服务状态
0 * * * * /path/to/health_check.sh >> /var/log/health_check.log 2>&1

# 每周日凌晨3点执行完整备份
0 3 * * 0 /path/to/full_backup.sh >> /var/log/backup.log 2>&1
```

### 🚨 告警配置 / Alert Configuration

**Prometheus告警规则 / Prometheus Alert Rules:**
```yaml
# monitoring/alert_rules.yml
groups:
- name: knowledge-platform
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is above 90%"

  - alert: DatabaseConnectionPoolExhausted
    expr: database_pool_size > 18
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Database connection pool nearly exhausted"
      description: "Connection pool usage is {{ $value }}/20"
```

---

## 故障排除 / Troubleshooting

### 🚨 常见问题 / Common Issues

#### 1. 服务启动失败 / Service Startup Failure

**问题症状 / Symptoms:**
```
Error: Failed to start service
Port already in use
Permission denied
```

**解决方案 / Solutions:**
```bash
# 检查端口占用
netstat -tulpn | grep :8000
lsof -i :8000

# 终止占用进程
kill -9 <PID>

# 检查权限
sudo chown -R $USER:$USER /path/to/project
chmod +x deployment/scripts/deploy.sh

# 检查防火墙
sudo ufw allow 8000
sudo ufw allow 3000
```

#### 2. 数据库连接问题 / Database Connection Issues

**问题症状 / Symptoms:**
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
Connection refused
Authentication failed
```

**解决方案 / Solutions:**
```bash
# 检查数据库服务状态
docker-compose ps mysql
kubectl get pods -l app=mysql -n knowledge-platform

# 检查数据库日志
docker-compose logs mysql
kubectl logs -l app=mysql -n knowledge-platform

# 测试数据库连接
mysql -h localhost -P 3306 -u app_user -p
psql -h localhost -p 5432 -U app_user -d knowledge_platform

# 重置数据库密码
docker-compose exec mysql mysql -u root -p -e "ALTER USER 'app_user'@'%' IDENTIFIED BY 'new_password';"
```

#### 3. 内存不足 / Out of Memory

**问题症状 / Symptoms:**
```
OOMKilled
Container killed due to memory limit
Process killed by system
```

**解决方案 / Solutions:**
```bash
# 检查内存使用
free -h
docker stats
kubectl top pods -n knowledge-platform

# 增加内存限制
# Docker Compose
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G

# Kubernetes
resources:
  limits:
    memory: "1Gi"

# 优化应用内存使用
# 减少连接池大小
DATABASE_POOL_SIZE = 10
# 启用内存缓存清理
CACHE_MAX_SIZE = 100
```

#### 4. 网络连接问题 / Network Connectivity Issues

**问题症状 / Symptoms:**
```
Connection timeout
Network unreachable
DNS resolution failed
```

**解决方案 / Solutions:**
```bash
# 检查网络连接
ping backend-service
nslookup backend-service
telnet backend-service 8000

# 检查Docker网络
docker network ls
docker network inspect knowledge-platform-network

# 检查Kubernetes网络
kubectl get networkpolicies -n knowledge-platform
kubectl describe service backend-service -n knowledge-platform

# 重启网络服务
docker-compose down && docker-compose up -d
kubectl rollout restart deployment/backend -n knowledge-platform
```

### 🔍 诊断工具 / Diagnostic Tools

**健康检查脚本 / Health Check Script:**
```bash
#!/bin/bash
# health_check.sh

echo "=== 知识管理平台健康检查 / Knowledge Platform Health Check ==="

# 检查服务状态
echo "检查服务状态... / Checking service status..."
curl -f http://localhost:8000/status || echo "后端服务异常 / Backend service error"
curl -f http://localhost:3000 || echo "前端服务异常 / Frontend service error"

# 检查数据库连接
echo "检查数据库连接... / Checking database connection..."
curl -f http://localhost:8000/api/v1/health || echo "数据库连接异常 / Database connection error"

# 检查WebSocket连接
echo "检查WebSocket连接... / Checking WebSocket connection..."
curl -f http://localhost:8000/api/v1/ws/stats || echo "WebSocket服务异常 / WebSocket service error"

# 检查磁盘空间
echo "检查磁盘空间... / Checking disk space..."
df -h | grep -E "(/$|/var|/tmp)" | awk '{if($5+0 > 80) print "警告: "$6" 磁盘使用率过高 "$5}'

# 检查内存使用
echo "检查内存使用... / Checking memory usage..."
free -m | awk 'NR==2{printf "内存使用率: %.2f%%\n", $3*100/$2}'

# 检查CPU使用
echo "检查CPU使用... / Checking CPU usage..."
top -bn1 | grep "Cpu(s)" | awk '{print "CPU使用率: "$2}'

echo "健康检查完成 / Health check completed"
```

**性能分析脚本 / Performance Analysis Script:**
```bash
#!/bin/bash
# performance_analysis.sh

echo "=== 性能分析报告 / Performance Analysis Report ==="

# API响应时间测试
echo "测试API响应时间... / Testing API response time..."
for i in {1..10}; do
    curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/status
done

# 数据库性能测试
echo "测试数据库性能... / Testing database performance..."
docker-compose exec mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "
    SELECT 
        SCHEMA_NAME as 'Database',
        ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) as 'Size (MB)'
    FROM information_schema.SCHEMATA 
    LEFT JOIN information_schema.TABLES ON SCHEMATA.SCHEMA_NAME = TABLES.TABLE_SCHEMA 
    WHERE SCHEMA_NAME = 'knowledge_platform'
    GROUP BY SCHEMA_NAME;
"

# 连接数统计
echo "统计连接数... / Counting connections..."
docker-compose exec mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "SHOW STATUS LIKE 'Threads_connected';"

# WebSocket连接统计
echo "统计WebSocket连接... / Counting WebSocket connections..."
curl -s http://localhost:8000/api/v1/ws/stats | jq .

echo "性能分析完成 / Performance analysis completed"
```

### 📞 获取支持 / Getting Support

**技术支持渠道 / Technical Support Channels:**

1. **文档中心 / Documentation Center**
   - 在线文档: https://docs.knowledge-platform.com
   - API文档: https://api.knowledge-platform.com/docs
   - 部署指南: https://docs.knowledge-platform.com/deployment

2. **社区支持 / Community Support**
   - GitHub Issues: https://github.com/knowledge-platform/issues
   - 讨论论坛: https://community.knowledge-platform.com
   - Stack Overflow: 标签 `knowledge-platform`

3. **商业支持 / Commercial Support**
   - 邮件支持: support@knowledge-platform.com
   - 企业支持: enterprise@knowledge-platform.com
   - 紧急支持: emergency@knowledge-platform.com

**问题报告模板 / Issue Report Template:**
```markdown
## 问题描述 / Problem Description
简要描述遇到的问题 / Brief description of the issue

## 环境信息 / Environment Information
- 操作系统 / OS: 
- 部署方式 / Deployment: 
- 数据库类型 / Database: 
- 版本信息 / Version: 

## 重现步骤 / Steps to Reproduce
1. 
2. 
3. 

## 期望结果 / Expected Result
描述期望的正常行为 / Description of expected behavior

## 实际结果 / Actual Result
描述实际发生的情况 / Description of what actually happened

## 日志信息 / Log Information
```
相关的错误日志 / Relevant error logs
```

## 附加信息 / Additional Information
其他可能有用的信息 / Any other useful information
```

---

## 📄 附录 / Appendix

### 🔗 相关链接 / Related Links

- **项目主页 / Project Homepage**: https://knowledge-platform.com
- **源码仓库 / Source Repository**: https://github.com/knowledge-platform/knowledge-management-platform
- **Docker镜像 / Docker Images**: https://hub.docker.com/r/knowledge-platform
- **Helm Chart仓库 / Helm Chart Repository**: https://charts.knowledge-platform.com

### 📋 版本兼容性 / Version Compatibility

| 组件 / Component | 最低版本 / Minimum | 推荐版本 / Recommended | 最新测试 / Latest Tested |
|-----------------|------------------|---------------------|----------------------|
| Python | 3.9 | 3.11 | 3.12 |
| Node.js | 16 | 18 LTS | 20 |
| Docker | 20.10 | 24.0 | 25.0 |
| Kubernetes | 1.20 | 1.28 | 1.29 |
| Helm | 3.0 | 3.12 | 3.14 |
| MySQL | 8.0 | 8.0 | 8.3 |
| PostgreSQL | 12 | 14 | 16 |
| MongoDB | 5.0 | 6.0 | 7.0 |
| Redis | 6.0 | 7.0 | 7.2 |

### 📝 更新日志 / Changelog

**v1.0.0 (2024-02-09)**
- ✅ 初始版本发布 / Initial release
- ✅ 支持多种部署方式 / Multiple deployment methods support
- ✅ 完整的数据库配置选项 / Complete database configuration options
- ✅ 生产就绪的安全特性 / Production-ready security features

---

**文档版本 / Document Version**: v1.0.0  
**最后更新 / Last Updated**: 2024-02-09  
**维护者 / Maintainer**: Knowledge Platform Team  
**许可证 / License**: MIT License