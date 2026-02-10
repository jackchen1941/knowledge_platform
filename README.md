# 🚀 知识管理平台 / Knowledge Management Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)](https://kubernetes.io/)
[![Security](https://img.shields.io/badge/Security-100%25-green.svg)](#security)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](#testing)

> 现代化的企业级知识管理平台，支持实时协作、智能搜索和多设备同步  
> Modern enterprise-grade knowledge management platform with real-time collaboration, intelligent search, and multi-device sync

## ✨ 核心特性 / Key Features

### 🔐 企业级安全 / Enterprise Security
- JWT令牌认证 + bcrypt密码加密
- 多层安全防护 (SQL注入、XSS、CSRF防护)
- 暴力破解保护 + 速率限制
- 完整安全审计日志

### 📚 智能知识管理 / Intelligent Knowledge Management
- Markdown内容支持 + 版本控制
- 全文搜索 + 智能建议
- 层级分类 + 彩色标签系统
- 字数统计 + 阅读时间计算
- **🆕 URL导入** - 从任何公开网页导入文章
- **🆕 多平台导入** - 支持CSDN、知乎、掘金、GitHub等

### 🌐 实时协作 / Real-time Collaboration
- WebSocket实时通信
- **🆕 多设备数据同步** - 手机、平板、电脑无缝同步
- 实时通知推送
- 在线状态显示
- **🆕 冲突检测与解决** - 智能处理多设备编辑冲突

### 🔄 多平台部署 / Multi-platform Deployment
- **一键部署** - 完全自动化
- **Docker支持** - 容器化部署
- **Kubernetes就绪** - 生产级编排
- **多数据库支持** - SQLite/MySQL/PostgreSQL/MongoDB

## 🚀 快速开始 / Quick Start

### 方式一：使用预构建 Docker 镜像 (最快速 🚀)

```bash
# 克隆项目
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 使用预构建镜像启动 (无需构建，直接运行)
docker-compose -f docker-compose.ghcr.yml up -d

# 查看日志
docker-compose -f docker-compose.ghcr.yml logs -f
```

**镜像地址**:
- Backend: `ghcr.io/jackchen1941/knowledge-platform-backend:latest`
- Frontend: `ghcr.io/jackchen1941/knowledge-platform-frontend:latest`

### 方式二：一键自动部署

```bash
# 克隆项目
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 一键启动 (自动检测环境并配置)
chmod +x quick-start.sh
./quick-start.sh
```

### 方式三：Docker 本地构建

```bash
# 完全自动化部署 (包含所有服务)
docker-compose -f deployment/docker-compose.auto.yml up -d

# 或选择特定数据库
docker-compose -f deployment/docker-compose.mysql.yml up -d
```

### 方式四：本地开发环境

```bash
# 后端 (使用 Python venv)
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install && npm start
```

## 🌐 访问地址 / Access URLs

部署完成后访问：

- **🎯 前端应用**: http://localhost:3000
- **🔧 后端API**: http://localhost:8000
- **📖 API文档**: http://localhost:8000/docs
- **🗄️ 数据库管理**: http://localhost:8080 (phpMyAdmin)
- **📊 系统监控**: http://localhost:3001 (Grafana)

**默认管理员账户**: `admin` / `admin123`

## 🏗️ 技术架构 / Technical Architecture

### 后端技术栈 / Backend Stack
- **FastAPI** - 现代异步Web框架
- **SQLAlchemy** - 异步ORM
- **WebSocket** - 实时通信
- **Redis** - 缓存和会话管理
- **JWT + bcrypt** - 安全认证

### 前端技术栈 / Frontend Stack
- **React 18** + **TypeScript** - 现代前端框架
- **Ant Design** - 企业级UI组件
- **Redux Toolkit** - 状态管理
- **WebSocket Client** - 实时通信

### 数据库支持 / Database Support
- **SQLite** - 本地开发
- **MySQL** - 生产环境
- **PostgreSQL** - 企业级
- **MongoDB** - 文档存储

## 📊 项目统计 / Project Statistics

- **📝 代码行数**: 37,000+ 行
- **🎯 功能模块**: 14 个核心模块
- **🔌 API端点**: 50+ 个
- **🧪 测试用例**: 100+ 个
- **🔒 安全测试**: 26项 (100%通过)
- **⚡ 性能**: < 300ms 响应时间

## 🔒 安全特性 / Security Features

### 🛡️ 多层防护 / Multi-layer Protection
- ✅ SQL注入防护
- ✅ XSS攻击防护
- ✅ CSRF保护
- ✅ 暴力破解保护
- ✅ 速率限制
- ✅ 输入验证和清理

### 📋 安全测试结果 / Security Test Results
```
🔒 安全测试总结:
✅ 通过: 26项
❌ 失败: 0项
⚠️ 警告: 2项 (非关键)
📊 成功率: 100%
```

## 🧪 测试 / Testing

### 运行测试 / Run Tests

```bash
# 运行所有测试 / Run all tests
python run_tests.py

# 运行特定类别的测试 / Run specific test category
python run_tests.py --category security    # 安全测试
python run_tests.py --category integration # 集成测试
python run_tests.py --category backend     # 后端单元测试
python run_tests.py --category system      # 系统测试
python run_tests.py --category feature     # 功能测试

# 后端单元测试 / Backend unit tests
cd backend
python -m pytest tests/ -v

# 安全测试 / Security tests
python tests/security/test_security_comprehensive.py
```

### 测试覆盖 / Test Coverage
- **功能测试**: 100% 通过
- **安全测试**: 100% 通过 (26/26)
- **性能测试**: 优秀级别
- **集成测试**: 全面覆盖

## 📦 部署选项 / Deployment Options

### 🖥️ 本地部署 / Local Deployment
适合个人开发和小团队

### 🐳 Docker部署 / Docker Deployment
适合测试环境和中小型生产环境

### ☸️ Kubernetes部署 / Kubernetes Deployment
适合大规模生产环境和企业部署

### ⚓ Helm Chart部署 / Helm Chart Deployment
适合企业级部署和管理

## 📚 文档 / Documentation

- **[快速开始指南](README_QUICKSTART.md)** - 一键部署指南
- **[部署指南](DEPLOYMENT_GUIDE.md)** - 详细部署文档
- **[Docker镜像指南](DOCKER_IMAGE_GUIDE.md)** - Docker镜像构建和使用 🐳
- **[快速测试部署](docs/QUICK_TEST_DEPLOYMENT.md)** - 在不同平台快速测试
- **[Git问题解决](docs/GIT_TROUBLESHOOTING.md)** - Git常见问题和解决方案
- **[API文档](http://localhost:8000/docs)** - 自动生成的API文档
- **[完整技术文档](docs/PROJECT_COMPLETE_DOCUMENTATION.md)** - 详细技术文档
- **[项目结构说明](PROJECT_STRUCTURE.md)** - 项目结构和目录说明
- **[实现细节文档](docs/implementation/)** - 各功能模块实现细节
- **[项目完成报告](docs/progress/FINAL_PROJECT_COMPLETION_REPORT.md)** - 完整项目报告

## � Docker 镜像 / Docker Images

### 预构建镜像 / Pre-built Images

我们提供了预构建的 Docker 镜像，可以直接使用：

```bash
# 拉取镜像
docker pull ghcr.io/jackchen1941/knowledge-platform-backend:latest
docker pull ghcr.io/jackchen1941/knowledge-platform-frontend:latest

# 使用 Docker Compose 启动
docker-compose -f docker-compose.ghcr.yml up -d
```

### 构建自己的镜像 / Build Your Own Images

```bash
# 构建镜像
./build-images.sh 1.0.0

# 推送到 GitHub Container Registry
./push-images.sh 1.0.0

# 或一键构建并推送
./build-and-push.sh 1.0.0
```

详细说明请查看 [Docker镜像指南](DOCKER_IMAGE_GUIDE.md)

## � 版本更新 / Version Updates

### 当前版本 / Current Version: v1.0.0

### 更新方式 / Update Method

**使用预构建镜像更新：**
```bash
# 拉取最新镜像
docker-compose -f docker-compose.ghcr.yml pull

# 重启服务
docker-compose -f docker-compose.ghcr.yml up -d
```

**从源码更新：**
```bash
# 拉取最新版本
git pull origin main

# 重新部署
./quick-start.sh

# 或使用Docker
docker-compose -f deployment/docker-compose.auto.yml up -d --build
```

## 🤝 贡献 / Contributing

我们欢迎所有形式的贡献！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证 / License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持 / Support

- **🐛 问题报告**: [GitHub Issues](https://github.com/jackchen1941/knowledge_platform/issues)
- **💬 讨论**: [GitHub Discussions](https://github.com/jackchen1941/knowledge_platform/discussions)
- **📦 容器镜像**: [GitHub Packages](https://github.com/jackchen1941?tab=packages)
- **📖 在线文档**: [项目文档](https://github.com/jackchen1941/knowledge_platform/tree/main/docs)

## 🌟 Star History
[![Star History Chart](https://api.star-history.com/svg?repos=your-username/knowledge-management-platform&type=Date)](https://star-history.com/#your-username/knowledge-management-platform&Date)

## 🎯 路线图 / Roadmap

### v1.1.0 (计划中)
- [ ] AI智能推荐
- [ ] 移动端适配
- [ ] 多语言支持
- [ ] 高级搜索功能

### v1.2.0 (计划中)
- [ ] 团队协作功能
- [ ] 第三方集成 (Slack, Teams)
- [ ] 高级分析报告
- [ ] 企业级SSO

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**

**⭐ If this project helps you, please give us a Star!**

Made with ❤️ by Knowledge Platform Team

</div>