# Docker 镜像构建与发布指南 / Docker Image Build & Publish Guide

## 📋 目录

- [技术栈版本](#技术栈版本)
- [本地开发环境](#本地开发环境)
- [Docker镜像构建](#docker镜像构建)
- [发布到GitHub Container Registry](#发布到github-container-registry)
- [使用预构建镜像](#使用预构建镜像)

---

## 🔧 技术栈版本

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 推荐使用 3.11 或更高版本 |
| FastAPI | 0.110.0+ | 现代异步Web框架 |
| SQLAlchemy | 2.0.25+ | ORM框架 |
| Uvicorn | 0.27.0+ | ASGI服务器 |
| Pydantic | 2.6.0+ | 数据验证 |
| Redis | 5.0.1+ | 缓存和消息队列 |
| Celery | 5.3.6+ | 异步任务队列 |
| Elasticsearch | 8.12.0+ | 全文搜索引擎 |

**核心依赖包：**
```txt
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
alembic>=1.13.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
redis>=5.0.1
elasticsearch>=8.12.0
```

### 前端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Node.js | 18+ | JavaScript运行时 |
| React | 18.2.0 | UI框架 |
| TypeScript | 5.2.2 | 类型安全 |
| Ant Design | 5.11.5 | UI组件库 |
| Redux Toolkit | 1.9.7 | 状态管理 |
| React Router | 6.18.0 | 路由管理 |
| Axios | 1.6.2 | HTTP客户端 |

**核心依赖包：**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.2.2",
  "antd": "^5.11.5",
  "@reduxjs/toolkit": "^1.9.7",
  "react-router-dom": "^6.18.0",
  "axios": "^1.6.2"
}
```

### 数据库支持

| 数据库 | 版本 | 驱动 |
|--------|------|------|
| PostgreSQL | 15+ | asyncpg>=0.29.0 |
| MySQL | 8.0+ | aiomysql>=0.2.0 |
| SQLite | 3.35+ | aiosqlite>=0.20.0 |
| MongoDB | 6.0+ | motor>=3.4.0 |

---

## 💻 本地开发环境

### 方式一：使用 Python venv（推荐用于开发）

#### 1. 创建虚拟环境

**Linux/macOS:**
```bash
# 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 创建虚拟环境
cd backend
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

**Windows:**
```cmd
# 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 创建虚拟环境
cd backend
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库等信息
nano .env  # 或使用其他编辑器
```

#### 3. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 初始化系统（创建管理员账户等）
python init_system.py
```

#### 4. 启动后端服务

```bash
# 开发模式（带热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（多进程）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 5. 前端开发环境

```bash
# 进入前端目录
cd ../frontend

# 安装依赖
npm install

# 启动开发服务器
npm start

# 构建生产版本
npm run build
```

### 方式二：使用 Docker Compose（推荐用于测试）

```bash
# 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🐳 Docker镜像构建

### 构建单个镜像

#### 后端镜像

```bash
# 进入后端目录
cd backend

# 构建镜像
docker build -t knowledge-platform-backend:latest .

# 指定版本标签
docker build -t knowledge-platform-backend:1.0.0 .

# 多平台构建（支持 ARM64 和 AMD64）
docker buildx build --platform linux/amd64,linux/arm64 \
  -t knowledge-platform-backend:latest .
```

#### 前端镜像

```bash
# 进入前端目录
cd frontend

# 构建镜像
docker build -t knowledge-platform-frontend:latest .

# 指定版本标签
docker build -t knowledge-platform-frontend:1.0.0 .

# 多平台构建
docker buildx build --platform linux/amd64,linux/arm64 \
  -t knowledge-platform-frontend:latest .
```

### 使用构建脚本

创建 `build-images.sh` 脚本：

```bash
#!/bin/bash

# 设置版本号
VERSION=${1:-latest}
REGISTRY="ghcr.io/jackchen1941"

echo "🚀 Building Knowledge Platform Docker Images - Version: $VERSION"

# 构建后端镜像
echo "📦 Building backend image..."
cd backend
docker build -t ${REGISTRY}/knowledge-platform-backend:${VERSION} .
docker tag ${REGISTRY}/knowledge-platform-backend:${VERSION} ${REGISTRY}/knowledge-platform-backend:latest
cd ..

# 构建前端镜像
echo "📦 Building frontend image..."
cd frontend
docker build -t ${REGISTRY}/knowledge-platform-frontend:${VERSION} .
docker tag ${REGISTRY}/knowledge-platform-frontend:${VERSION} ${REGISTRY}/knowledge-platform-frontend:latest
cd ..

echo "✅ Build completed!"
echo ""
echo "Images built:"
echo "  - ${REGISTRY}/knowledge-platform-backend:${VERSION}"
echo "  - ${REGISTRY}/knowledge-platform-backend:latest"
echo "  - ${REGISTRY}/knowledge-platform-frontend:${VERSION}"
echo "  - ${REGISTRY}/knowledge-platform-frontend:latest"
```

使用脚本：

```bash
# 赋予执行权限
chmod +x build-images.sh

# 构建 latest 版本
./build-images.sh

# 构建指定版本
./build-images.sh 1.0.0
```

---

## 📤 发布到GitHub Container Registry

### 1. 配置GitHub Personal Access Token

1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - `write:packages` - 上传镜像
   - `read:packages` - 下载镜像
   - `delete:packages` - 删除镜像（可选）
4. 生成并保存 token

### 2. 登录到GitHub Container Registry

```bash
# 使用 token 登录
echo $GITHUB_TOKEN | docker login ghcr.io -u jackchen1941 --password-stdin

# 或者交互式登录
docker login ghcr.io -u jackchen1941
# 输入 token 作为密码
```

### 3. 推送镜像

#### 手动推送

```bash
# 设置变量
REGISTRY="ghcr.io/jackchen1941"
VERSION="1.0.0"

# 推送后端镜像
docker push ${REGISTRY}/knowledge-platform-backend:${VERSION}
docker push ${REGISTRY}/knowledge-platform-backend:latest

# 推送前端镜像
docker push ${REGISTRY}/knowledge-platform-frontend:${VERSION}
docker push ${REGISTRY}/knowledge-platform-frontend:latest
```

#### 使用推送脚本

创建 `push-images.sh` 脚本：

```bash
#!/bin/bash

# 设置版本号
VERSION=${1:-latest}
REGISTRY="ghcr.io/jackchen1941"

echo "🚀 Pushing Knowledge Platform Docker Images - Version: $VERSION"

# 检查是否已登录
if ! docker info | grep -q "Username: jackchen1941"; then
    echo "❌ Not logged in to GitHub Container Registry"
    echo "Please run: docker login ghcr.io -u jackchen1941"
    exit 1
fi

# 推送后端镜像
echo "📤 Pushing backend image..."
docker push ${REGISTRY}/knowledge-platform-backend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${REGISTRY}/knowledge-platform-backend:latest
fi

# 推送前端镜像
echo "📤 Pushing frontend image..."
docker push ${REGISTRY}/knowledge-platform-frontend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${REGISTRY}/knowledge-platform-frontend:latest
fi

echo "✅ Push completed!"
echo ""
echo "Images available at:"
echo "  - ${REGISTRY}/knowledge-platform-backend:${VERSION}"
echo "  - ${REGISTRY}/knowledge-platform-frontend:${VERSION}"
```

使用脚本：

```bash
# 赋予执行权限
chmod +x push-images.sh

# 推送 latest 版本
./push-images.sh

# 推送指定版本
./push-images.sh 1.0.0
```

### 4. 设置镜像为公开

1. 访问 https://github.com/jackchen1941?tab=packages
2. 选择镜像包
3. 点击 "Package settings"
4. 在 "Danger Zone" 中选择 "Change visibility"
5. 设置为 "Public"

### 5. 完整的构建和推送流程

创建 `build-and-push.sh` 脚本：

```bash
#!/bin/bash

set -e  # 遇到错误立即退出

# 设置版本号
VERSION=${1:-latest}
REGISTRY="ghcr.io/jackchen1941"

echo "🚀 Building and Pushing Knowledge Platform Docker Images"
echo "Version: $VERSION"
echo "Registry: $REGISTRY"
echo ""

# 检查是否已登录
if ! docker info | grep -q "Username: jackchen1941"; then
    echo "❌ Not logged in to GitHub Container Registry"
    echo "Please run: docker login ghcr.io -u jackchen1941"
    exit 1
fi

# 构建后端镜像
echo "📦 Building backend image..."
cd backend
docker build -t ${REGISTRY}/knowledge-platform-backend:${VERSION} .
if [ "$VERSION" != "latest" ]; then
    docker tag ${REGISTRY}/knowledge-platform-backend:${VERSION} ${REGISTRY}/knowledge-platform-backend:latest
fi
cd ..

# 构建前端镜像
echo "📦 Building frontend image..."
cd frontend
docker build -t ${REGISTRY}/knowledge-platform-frontend:${VERSION} .
if [ "$VERSION" != "latest" ]; then
    docker tag ${REGISTRY}/knowledge-platform-frontend:${VERSION} ${REGISTRY}/knowledge-platform-frontend:latest
fi
cd ..

# 推送后端镜像
echo "📤 Pushing backend image..."
docker push ${REGISTRY}/knowledge-platform-backend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${REGISTRY}/knowledge-platform-backend:latest
fi

# 推送前端镜像
echo "📤 Pushing frontend image..."
docker push ${REGISTRY}/knowledge-platform-frontend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${REGISTRY}/knowledge-platform-frontend:latest
fi

echo ""
echo "✅ Build and push completed successfully!"
echo ""
echo "📦 Images available at:"
echo "  Backend:"
echo "    - ${REGISTRY}/knowledge-platform-backend:${VERSION}"
echo "    - ${REGISTRY}/knowledge-platform-backend:latest"
echo "  Frontend:"
echo "    - ${REGISTRY}/knowledge-platform-frontend:${VERSION}"
echo "    - ${REGISTRY}/knowledge-platform-frontend:latest"
echo ""
echo "🔗 View packages at: https://github.com/jackchen1941?tab=packages"
```

使用脚本：

```bash
# 赋予执行权限
chmod +x build-and-push.sh

# 构建并推送 latest 版本
./build-and-push.sh

# 构建并推送指定版本
./build-and-push.sh 1.0.0
```

---

## 🎯 使用预构建镜像

### 方式一：使用 Docker Compose（推荐）

创建 `docker-compose.ghcr.yml`：

```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/jackchen1941/knowledge-platform-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/knowledge_platform
      - REDIS_URL=redis://redis:6379/0
      - ELASTICSEARCH_URL=http://elasticsearch:9200
    depends_on:
      - postgres
      - redis
      - elasticsearch
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    image: ghcr.io/jackchen1941/knowledge-platform-frontend:latest
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=knowledge_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
```

启动服务：

```bash
# 拉取最新镜像
docker-compose -f docker-compose.ghcr.yml pull

# 启动服务
docker-compose -f docker-compose.ghcr.yml up -d

# 查看日志
docker-compose -f docker-compose.ghcr.yml logs -f

# 停止服务
docker-compose -f docker-compose.ghcr.yml down
```

### 方式二：直接运行容器

```bash
# 创建网络
docker network create kmp-network

# 启动 PostgreSQL
docker run -d --name postgres \
  --network kmp-network \
  -e POSTGRES_DB=knowledge_platform \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# 启动 Redis
docker run -d --name redis \
  --network kmp-network \
  -v redis_data:/data \
  redis:7-alpine

# 启动 Elasticsearch
docker run -d --name elasticsearch \
  --network kmp-network \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -v elasticsearch_data:/usr/share/elasticsearch/data \
  elasticsearch:8.11.0

# 启动后端
docker run -d --name backend \
  --network kmp-network \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/knowledge_platform \
  -e REDIS_URL=redis://redis:6379/0 \
  -e ELASTICSEARCH_URL=http://elasticsearch:9200 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/jackchen1941/knowledge-platform-backend:latest

# 启动前端
docker run -d --name frontend \
  --network kmp-network \
  -p 3000:80 \
  ghcr.io/jackchen1941/knowledge-platform-frontend:latest
```

### 方式三：使用特定版本

```bash
# 使用特定版本的镜像
docker-compose -f docker-compose.ghcr.yml pull

# 或者在 docker-compose.ghcr.yml 中指定版本
# image: ghcr.io/jackchen1941/knowledge-platform-backend:1.0.0
```

---

## 🔄 CI/CD 自动化

### GitHub Actions 自动构建和推送

在 `.github/workflows/docker-publish.yml` 中添加：

```yaml
name: Docker Image CI/CD

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME_BACKEND: ${{ github.repository }}-backend
  IMAGE_NAME_FRONTEND: ${{ github.repository }}-frontend

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata for backend
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}

      - name: Extract metadata for frontend
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
```

---

## 📊 镜像大小优化

当前镜像大小：
- 后端镜像：~500MB（使用多阶段构建）
- 前端镜像：~50MB（使用 Nginx Alpine）

优化建议：
1. ✅ 使用多阶段构建
2. ✅ 使用 Alpine 基础镜像
3. ✅ 清理不必要的文件
4. ✅ 使用 .dockerignore
5. ✅ 合并 RUN 命令减少层数

---

## 🔍 镜像验证

### 检查镜像

```bash
# 查看本地镜像
docker images | grep knowledge-platform

# 检查镜像详情
docker inspect ghcr.io/jackchen1941/knowledge-platform-backend:latest

# 查看镜像历史
docker history ghcr.io/jackchen1941/knowledge-platform-backend:latest
```

### 测试镜像

```bash
# 快速测试后端
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=sqlite+aiosqlite:///./test.db \
  ghcr.io/jackchen1941/knowledge-platform-backend:latest

# 快速测试前端
docker run --rm -p 3000:80 \
  ghcr.io/jackchen1941/knowledge-platform-frontend:latest

# 访问测试
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 📝 版本管理

### 语义化版本

遵循 [Semantic Versioning](https://semver.org/)：

- **MAJOR.MINOR.PATCH** (例如：1.0.0)
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

### 标签策略

```bash
# latest - 最新稳定版本
ghcr.io/jackchen1941/knowledge-platform-backend:latest

# 具体版本
ghcr.io/jackchen1941/knowledge-platform-backend:1.0.0
ghcr.io/jackchen1941/knowledge-platform-backend:1.0
ghcr.io/jackchen1941/knowledge-platform-backend:1

# 开发版本
ghcr.io/jackchen1941/knowledge-platform-backend:dev
ghcr.io/jackchen1941/knowledge-platform-backend:main
```

---

## 🎓 最佳实践

### 开发流程

1. **本地开发**: 使用 venv + 本地数据库
2. **本地测试**: 使用 Docker Compose
3. **构建镜像**: 使用构建脚本
4. **推送镜像**: 推送到 GHCR
5. **部署测试**: 使用预构建镜像

### 部署选择

| 场景 | 推荐方式 | 优点 |
|------|---------|------|
| 开发调试 | venv + 源码 | 快速迭代，方便调试 |
| 本地测试 | Docker Compose | 环境一致，快速启动 |
| 生产部署 | 预构建镜像 | 稳定可靠，快速部署 |
| 云端部署 | Kubernetes + 镜像 | 高可用，自动扩展 |

---

## 🆘 常见问题

### Q1: 如何更新镜像？

```bash
# 拉取最新镜像
docker pull ghcr.io/jackchen1941/knowledge-platform-backend:latest

# 重启容器
docker-compose -f docker-compose.ghcr.yml up -d
```

### Q2: 如何查看镜像版本？

```bash
# 查看镜像标签
docker images ghcr.io/jackchen1941/knowledge-platform-backend

# 查看镜像元数据
docker inspect ghcr.io/jackchen1941/knowledge-platform-backend:latest | grep -A 5 Labels
```

### Q3: 如何回滚到旧版本？

```bash
# 使用特定版本
docker-compose -f docker-compose.ghcr.yml down
# 修改 docker-compose.ghcr.yml 中的镜像版本
docker-compose -f docker-compose.ghcr.yml up -d
```

---

## 📚 相关文档

- [README.md](README.md) - 项目概述
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
- [docs/QUICK_TEST_DEPLOYMENT.md](docs/QUICK_TEST_DEPLOYMENT.md) - 快速测试
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

**文档版本**: 1.0.0  
**最后更新**: 2024-02-10  
**维护者**: jackchen1941
