# 🚀 知识管理平台 - 快速开始指南
# Knowledge Management Platform - Quick Start Guide

## 📋 一键部署 / One-Click Deployment

### 🎯 超简单部署 / Super Simple Deployment

**只需要一个命令！/ Just one command!**

```bash
# 下载并运行一键部署脚本
curl -sSL https://raw.githubusercontent.com/knowledge-platform/quick-start.sh | bash

# 或者克隆项目后运行
git clone <repository-url>
cd knowledge-management-platform
./quick-start.sh
```

### 🔧 系统要求 / System Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **内存 / RAM**: 4GB+ (推荐 8GB)
- **磁盘空间 / Disk**: 5GB+
- **操作系统 / OS**: Linux, macOS, Windows (WSL2)

### 🎨 部署选项 / Deployment Options

运行 `./quick-start.sh` 后，选择部署模式：

1. **🚀 完全自动化 (推荐)** - 包含所有服务和监控
2. **🐬 MySQL数据库** - 生产级MySQL数据库
3. **🗄️ SQLite数据库** - 轻量级本地数据库
4. **🍃 MongoDB数据库** - 文档数据库
5. **📊 包含监控系统** - 完整监控和管理工具

### ⚡ 自动化特性 / Automated Features

- ✅ **自动环境检测** - 智能选择最佳配置
- ✅ **自动数据库初始化** - 创建表结构和初始数据
- ✅ **自动依赖管理** - 处理所有服务依赖
- ✅ **自动健康检查** - 确保所有服务正常运行
- ✅ **自动错误恢复** - Redis连接失败时自动降级
- ✅ **自动安全配置** - 生产级安全设置

## 🌐 访问地址 / Access URLs

部署完成后，您可以访问：

### 🎯 主要服务 / Main Services
- **前端应用 / Frontend**: http://localhost:3000
- **后端API / Backend**: http://localhost:8000
- **API文档 / API Docs**: http://localhost:8000/docs

### 🛠️ 管理工具 / Management Tools
- **数据库管理 / Database**: http://localhost:8080 (phpMyAdmin)
- **Redis管理 / Redis**: http://localhost:8081 (Redis Commander)
- **系统监控 / Monitoring**: http://localhost:3001 (Grafana)
- **指标收集 / Metrics**: http://localhost:9090 (Prometheus)

### 🔑 默认账户 / Default Accounts

**应用管理员 / Application Admin:**
- 用户名 / Username: `admin`
- 密码 / Password: `admin123`

**数据库管理 / Database Admin:**
- 用户名 / Username: `root`
- 密码 / Password: `auto_root_password_123`

**监控系统 / Monitoring:**
- 用户名 / Username: `admin`
- 密码 / Password: `admin123`

## 📱 快速体验 / Quick Experience

### 1. 注册新用户 / Register New User
访问 http://localhost:3000，点击"注册"创建账户

### 2. 创建知识条目 / Create Knowledge Item
登录后，点击"新建"创建您的第一个知识条目

### 3. 体验搜索 / Try Search
使用搜索功能查找您的内容

### 4. 实时通信 / Real-time Communication
打开多个浏览器标签页，体验实时WebSocket通信

## 🔧 管理命令 / Management Commands

部署完成后，会自动创建管理脚本：

```bash
# 查看服务状态
./status.sh

# 查看日志
./logs.sh

# 重启服务
./restart.sh

# 停止服务
./stop.sh
```

### 手动Docker命令 / Manual Docker Commands

```bash
# 查看运行状态
docker-compose -f deployment/docker-compose.auto.yml ps

# 查看日志
docker-compose -f deployment/docker-compose.auto.yml logs -f

# 重启特定服务
docker-compose -f deployment/docker-compose.auto.yml restart backend

# 停止所有服务
docker-compose -f deployment/docker-compose.auto.yml down

# 完全清理（包括数据）
docker-compose -f deployment/docker-compose.auto.yml down -v
```

## 🐛 故障排除 / Troubleshooting

### 常见问题 / Common Issues

**1. 端口被占用 / Port Already in Use**
```bash
# 查看端口占用
lsof -i :8000
lsof -i :3000

# 停止占用进程
kill -9 <PID>
```

**2. Docker权限问题 / Docker Permission Issues**
```bash
# 添加用户到docker组
sudo usermod -aG docker $USER
# 重新登录或运行
newgrp docker
```

**3. 服务启动失败 / Service Startup Failed**
```bash
# 查看详细日志
docker-compose -f deployment/docker-compose.auto.yml logs backend
docker-compose -f deployment/docker-compose.auto.yml logs mysql
```

**4. 数据库连接失败 / Database Connection Failed**
```bash
# 检查MySQL状态
docker-compose -f deployment/docker-compose.auto.yml exec mysql mysql -u root -p -e "SHOW DATABASES;"

# 重启数据库服务
docker-compose -f deployment/docker-compose.auto.yml restart mysql
```

**5. Redis连接失败 / Redis Connection Failed**
```bash
# 检查Redis状态
docker-compose -f deployment/docker-compose.auto.yml exec redis redis-cli ping

# 重启Redis服务
docker-compose -f deployment/docker-compose.auto.yml restart redis
```

### 健康检查 / Health Check

```bash
# 检查系统状态
curl http://localhost:8000/status | jq

# 检查功能列表
curl http://localhost:8000/features | jq

# 检查WebSocket统计
curl http://localhost:8000/api/v1/ws/stats | jq
```

## 🔄 更新升级 / Updates & Upgrades

### 更新到最新版本 / Update to Latest Version

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose -f deployment/docker-compose.auto.yml up -d --build

# 运行数据库迁移（如果需要）
docker-compose -f deployment/docker-compose.auto.yml exec backend python -c "from app.core.database_init import initialize_database_sync; initialize_database_sync()"
```

### 备份数据 / Backup Data

```bash
# 备份MySQL数据库
docker-compose -f deployment/docker-compose.auto.yml exec mysql mysqldump -u root -pauto_root_password_123 knowledge_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份上传文件
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/uploads/

# 备份配置文件
cp -r deployment/ config_backup_$(date +%Y%m%d_%H%M%S)/
```

## 🚀 生产部署 / Production Deployment

### 安全配置 / Security Configuration

1. **更改默认密码 / Change Default Passwords**
2. **启用HTTPS / Enable HTTPS**
3. **配置防火墙 / Configure Firewall**
4. **设置备份策略 / Set Backup Strategy**

### 性能优化 / Performance Optimization

1. **增加资源限制 / Increase Resource Limits**
2. **启用缓存 / Enable Caching**
3. **配置负载均衡 / Configure Load Balancing**
4. **优化数据库 / Optimize Database**

## 📞 获取帮助 / Get Help

- **文档中心 / Documentation**: https://docs.knowledge-platform.com
- **GitHub Issues**: https://github.com/knowledge-platform/issues
- **社区论坛 / Community**: https://community.knowledge-platform.com
- **邮件支持 / Email**: support@knowledge-platform.com

## 🎉 开始使用 / Start Using

现在您已经成功部署了知识管理平台！

1. 访问 http://localhost:3000 开始使用
2. 使用默认管理员账户登录
3. 创建您的第一个知识条目
4. 探索所有功能特性

**祝您使用愉快！/ Enjoy using the platform!** 🎊