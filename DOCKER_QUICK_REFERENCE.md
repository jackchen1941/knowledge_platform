# Docker 快速参考 / Docker Quick Reference

## 🚀 快速开始 / Quick Start

### 使用预构建镜像（最快）

```bash
# 1. 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 2. 启动所有服务
docker-compose -f docker-compose.ghcr.yml up -d

# 3. 访问应用
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

## 📦 镜像地址 / Image URLs

```bash
# 后端镜像
ghcr.io/jackchen1941/knowledge-platform-backend:latest
ghcr.io/jackchen1941/knowledge-platform-backend:1.0.0

# 前端镜像
ghcr.io/jackchen1941/knowledge-platform-frontend:latest
ghcr.io/jackchen1941/knowledge-platform-frontend:1.0.0
```

## 🔧 常用命令 / Common Commands

### 启动服务

```bash
# 启动所有服务
docker-compose -f docker-compose.ghcr.yml up -d

# 启动并查看日志
docker-compose -f docker-compose.ghcr.yml up

# 仅启动特定服务
docker-compose -f docker-compose.ghcr.yml up -d backend frontend
```

### 查看状态

```bash
# 查看运行中的容器
docker-compose -f docker-compose.ghcr.yml ps

# 查看日志
docker-compose -f docker-compose.ghcr.yml logs

# 查看特定服务日志
docker-compose -f docker-compose.ghcr.yml logs -f backend

# 实时查看所有日志
docker-compose -f docker-compose.ghcr.yml logs -f
```

### 停止和清理

```bash
# 停止服务
docker-compose -f docker-compose.ghcr.yml stop

# 停止并删除容器
docker-compose -f docker-compose.ghcr.yml down

# 停止并删除容器和数据卷
docker-compose -f docker-compose.ghcr.yml down -v

# 停止并删除所有（包括镜像）
docker-compose -f docker-compose.ghcr.yml down -v --rmi all
```

### 更新镜像

```bash
# 拉取最新镜像
docker-compose -f docker-compose.ghcr.yml pull

# 重启服务
docker-compose -f docker-compose.ghcr.yml up -d

# 或一步完成
docker-compose -f docker-compose.ghcr.yml pull && \
docker-compose -f docker-compose.ghcr.yml up -d
```

### 进入容器

```bash
# 进入后端容器
docker-compose -f docker-compose.ghcr.yml exec backend bash

# 进入前端容器
docker-compose -f docker-compose.ghcr.yml exec frontend sh

# 进入数据库容器
docker-compose -f docker-compose.ghcr.yml exec postgres psql -U postgres
```

## 🛠️ 构建自己的镜像 / Build Your Own Images

### 本地构建

```bash
# 构建所有镜像
./build-images.sh

# 构建指定版本
./build-images.sh 1.0.0

# 仅构建后端
cd backend
docker build -t my-backend:latest .

# 仅构建前端
cd frontend
docker build -t my-frontend:latest .
```

### 推送到 GitHub Container Registry

```bash
# 1. 登录 GHCR
docker login ghcr.io -u jackchen1941

# 2. 构建并推送
./build-and-push.sh 1.0.0

# 或分步执行
./build-images.sh 1.0.0
./push-images.sh 1.0.0
```

## 🔍 故障排查 / Troubleshooting

### 检查服务健康状态

```bash
# 检查所有容器状态
docker-compose -f docker-compose.ghcr.yml ps

# 检查后端健康
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000
```

### 查看详细日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.ghcr.yml logs

# 查看最近100行日志
docker-compose -f docker-compose.ghcr.yml logs --tail=100

# 实时查看后端日志
docker-compose -f docker-compose.ghcr.yml logs -f backend

# 查看错误日志
docker-compose -f docker-compose.ghcr.yml logs | grep -i error
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.ghcr.yml restart

# 重启特定服务
docker-compose -f docker-compose.ghcr.yml restart backend

# 强制重新创建容器
docker-compose -f docker-compose.ghcr.yml up -d --force-recreate
```

### 清理和重置

```bash
# 清理未使用的容器
docker container prune

# 清理未使用的镜像
docker image prune

# 清理未使用的数据卷
docker volume prune

# 清理所有未使用的资源
docker system prune -a

# 完全重置（删除所有数据）
docker-compose -f docker-compose.ghcr.yml down -v
docker system prune -a -f
docker-compose -f docker-compose.ghcr.yml up -d
```

## 📊 性能监控 / Performance Monitoring

### 查看资源使用

```bash
# 查看所有容器资源使用
docker stats

# 查看特定容器资源使用
docker stats kmp-backend kmp-frontend

# 查看容器详细信息
docker inspect kmp-backend
```

### 数据库管理

```bash
# 连接到 PostgreSQL
docker-compose -f docker-compose.ghcr.yml exec postgres psql -U postgres -d knowledge_platform

# 备份数据库
docker-compose -f docker-compose.ghcr.yml exec postgres pg_dump -U postgres knowledge_platform > backup.sql

# 恢复数据库
docker-compose -f docker-compose.ghcr.yml exec -T postgres psql -U postgres knowledge_platform < backup.sql
```

## 🔐 安全配置 / Security Configuration

### 修改默认密码

编辑 `docker-compose.ghcr.yml`:

```yaml
environment:
  # 修改数据库密码
  - POSTGRES_PASSWORD=your-secure-password
  
  # 修改 JWT 密钥
  - JWT_SECRET_KEY=your-jwt-secret-key
  
  # 修改应用密钥
  - SECRET_KEY=your-app-secret-key
```

### 使用环境变量文件

创建 `.env` 文件：

```bash
# 数据库配置
POSTGRES_PASSWORD=your-secure-password
POSTGRES_USER=postgres
POSTGRES_DB=knowledge_platform

# 应用配置
SECRET_KEY=your-app-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DEBUG=false

# Redis配置
REDIS_PASSWORD=your-redis-password
```

然后在 docker-compose.ghcr.yml 中引用：

```yaml
services:
  backend:
    env_file:
      - .env
```

## 🌐 生产环境部署 / Production Deployment

### 使用 HTTPS

1. 获取 SSL 证书（Let's Encrypt）
2. 配置 Nginx 反向代理
3. 更新 docker-compose.ghcr.yml

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
```

### 扩展服务

```bash
# 扩展后端服务到3个实例
docker-compose -f docker-compose.ghcr.yml up -d --scale backend=3

# 扩展 Celery Worker
docker-compose -f docker-compose.ghcr.yml up -d --scale celery-worker=5
```

## 📚 相关文档 / Related Documentation

- [完整 Docker 镜像指南](DOCKER_IMAGE_GUIDE.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [快速测试部署](docs/QUICK_TEST_DEPLOYMENT.md)
- [项目主文档](README.md)

## 💡 提示 / Tips

1. **首次启动较慢**: 需要下载镜像和初始化数据库，请耐心等待
2. **端口冲突**: 如果端口被占用，修改 docker-compose.ghcr.yml 中的端口映射
3. **数据持久化**: 数据存储在 Docker volumes 中，删除容器不会丢失数据
4. **日志查看**: 使用 `-f` 参数实时查看日志，Ctrl+C 退出
5. **资源限制**: 可以在 docker-compose.ghcr.yml 中添加资源限制

## 🆘 获取帮助 / Get Help

- [GitHub Issues](https://github.com/jackchen1941/knowledge_platform/issues)
- [GitHub Discussions](https://github.com/jackchen1941/knowledge_platform/discussions)
- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)

---

**最后更新**: 2024-02-10  
**版本**: 1.0.0
