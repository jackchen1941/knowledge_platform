# 🚀 全新部署指南 / Fresh Deployment Guide

> 本指南适用于首次部署或完全重新部署知识管理平台

## 📋 目录 / Table of Contents

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [数据库初始化](#数据库初始化)
- [验证部署](#验证部署)
- [常见问题](#常见问题)

---

## 🖥️ 系统要求 / System Requirements

### 最低配置 / Minimum Requirements
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **内存**: 4GB RAM
- **磁盘空间**: 2GB
- **Python**: 3.9+
- **Node.js**: 16+
- **数据库**: SQLite (默认) / MySQL 8.0+ / PostgreSQL 13+

### 推荐配置 / Recommended Requirements
- **内存**: 8GB+ RAM
- **磁盘空间**: 10GB+
- **Python**: 3.10+
- **Node.js**: 18+

---

## ⚡ 快速开始 / Quick Start

### 方式一：一键自动部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 2. 运行一键部署脚本
chmod +x quick-start.sh
./quick-start.sh

# 3. 等待部署完成，访问 http://localhost:3000
```

**默认管理员账户**:
- 用户名: `admin@knowledge-platform.com`
- 密码: `admin123`

### 方式二：Docker 部署

```bash
# 使用预构建镜像（最快）
docker-compose -f docker-compose.ghcr.yml up -d

# 或本地构建
docker-compose up -d
```

---

## 📝 详细步骤 / Detailed Steps

### 步骤 1: 环境准备

#### 1.1 安装 Python 3.9+

**macOS**:
```bash
brew install python@3.10
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**Windows**:
下载并安装: https://www.python.org/downloads/

#### 1.2 安装 Node.js 16+

**macOS**:
```bash
brew install node
```

**Ubuntu/Debian**:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows**:
下载并安装: https://nodejs.org/

#### 1.3 验证安装

```bash
python3 --version  # 应显示 3.9+
node --version     # 应显示 16+
npm --version      # 应显示 8+
```

### 步骤 2: 克隆项目

```bash
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform
```

### 步骤 3: 后端部署

#### 3.1 创建虚拟环境

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

#### 3.2 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.3 配置环境变量（可选）

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置（可选，默认使用SQLite）
nano .env
```

**默认配置**:
```env
# 数据库配置（默认SQLite，无需修改）
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./knowledge_platform.db

# JWT密钥（生产环境请修改）
SECRET_KEY=your-secret-key-here

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

#### 3.4 初始化数据库

数据库会在首次启动时自动初始化，包括：
- ✅ 创建所有表结构
- ✅ 创建默认管理员账户
- ✅ 创建默认分类和标签

```bash
# 启动后端服务（会自动初始化数据库）
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**首次启动日志示例**:
```
INFO: 开始初始化数据库... / Starting database initialization...
INFO: SQLite数据库路径: ./knowledge_platform.db
INFO: 首次迁移，创建所有表... / First migration, creating all tables...
INFO: 表结构创建完成 / Table structure created
INFO: 创建默认管理员用户: admin / Created default admin user: admin
INFO: 创建默认分类 / Created default categories
INFO: 创建默认标签 / Created default tags
INFO: 数据库初始化完成 / Database initialization completed
INFO: Application startup complete.
```

### 步骤 4: 前端部署

打开新终端窗口：

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

前端会自动在浏览器中打开 http://localhost:3000

### 步骤 5: 验证部署

#### 5.1 检查服务状态

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **前端应用**: http://localhost:3000

#### 5.2 登录测试

使用默认管理员账户登录：
- **邮箱**: `admin@knowledge-platform.com`
- **密码**: `admin123`

#### 5.3 功能测试

1. ✅ 创建知识条目
2. ✅ 添加分类和标签
3. ✅ 搜索功能
4. ✅ URL导入功能
5. ✅ 用户管理（管理员）

---

## 🗄️ 数据库初始化 / Database Initialization

### 自动初始化机制

系统在首次启动时会自动检测并初始化数据库：

```python
# 初始化流程
1. 检查数据库是否存在
   ├─ 不存在 → 创建数据库
   └─ 存在 → 继续

2. 检查表结构是否存在
   ├─ 不存在 → 创建所有表
   └─ 存在 → 检查是否需要迁移

3. 检查是否有初始数据
   ├─ 无数据 → 创建默认数据
   │   ├─ 管理员账户
   │   ├─ 默认分类
   │   └─ 默认标签
   └─ 有数据 → 跳过初始化
```

### 手动初始化（如果需要）

```bash
cd backend

# 方式1: 使用Python脚本
python -c "from app.core.database_init import initialize_database_sync; initialize_database_sync()"

# 方式2: 使用CLI命令
python -m app.cli.database init

# 方式3: 创建管理员用户
python create_admin.py
```

### 重置数据库

如果需要完全重置数据库：

```bash
cd backend

# 1. 停止后端服务 (Ctrl+C)

# 2. 删除数据库文件
rm knowledge_platform.db
rm knowledge_platform.db-shm
rm knowledge_platform.db-wal

# 3. 重新启动服务（会自动重新初始化）
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 默认数据说明

#### 管理员账户
- **用户名**: admin
- **邮箱**: admin@knowledge-platform.com
- **密码**: admin123
- **权限**: 超级管理员

#### 默认分类
1. 技术文档 (蓝色)
2. 项目管理 (绿色)
3. 学习笔记 (橙色)
4. 工作流程 (紫色)
5. 其他 (灰色)

#### 默认标签
1. 重要 (红色)
2. 待办 (橙色)
3. 已完成 (绿色)
4. 参考 (蓝色)
5. 草稿 (灰色)

---

## ✅ 验证部署 / Verify Deployment

### 检查清单

```bash
# 1. 检查后端服务
curl http://localhost:8000/health
# 预期输出: {"status":"healthy"}

# 2. 检查API文档
open http://localhost:8000/docs  # macOS
# 或在浏览器中访问

# 3. 检查前端服务
curl http://localhost:3000
# 应返回HTML内容

# 4. 检查数据库
cd backend
ls -lh knowledge_platform.db
# 应显示数据库文件（大小 > 0）

# 5. 测试登录API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@knowledge-platform.com","password":"admin123"}'
# 应返回JWT token
```

### 功能验证

1. **用户认证** ✅
   - 登录成功
   - Token有效
   - 权限正确

2. **知识管理** ✅
   - 创建知识
   - 编辑知识
   - 删除知识
   - 查看知识

3. **分类标签** ✅
   - 查看分类
   - 查看标签
   - 关联知识

4. **搜索功能** ✅
   - 全文搜索
   - 过滤排序

5. **URL导入** ✅
   - 单个导入
   - 批量导入

6. **用户管理** ✅ (管理员)
   - 查看用户列表
   - 创建用户
   - 编辑用户
   - 删除用户

---

## ❓ 常见问题 / Common Issues

### 问题 1: 端口被占用

**错误信息**:
```
Error: Address already in use
```

**解决方案**:
```bash
# 查找占用端口的进程
# macOS/Linux:
lsof -i :8000  # 后端
lsof -i :3000  # 前端

# Windows:
netstat -ano | findstr :8000

# 杀死进程或更改端口
# 后端:
uvicorn app.main:app --port 8001

# 前端:
PORT=3001 npm start
```

### 问题 2: 数据库初始化失败

**错误信息**:
```
Database initialization failed
```

**解决方案**:
```bash
# 1. 检查数据库文件权限
ls -l backend/knowledge_platform.db

# 2. 手动删除并重新初始化
cd backend
rm -f knowledge_platform.db*
python -c "from app.core.database_init import initialize_database_sync; initialize_database_sync()"

# 3. 检查日志
tail -f backend/logs/app.log
```

### 问题 3: Python依赖安装失败

**错误信息**:
```
ERROR: Could not install packages
```

**解决方案**:
```bash
# 1. 升级pip
pip install --upgrade pip setuptools wheel

# 2. 使用国内镜像（中国用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 单独安装失败的包
pip install <package-name> --no-cache-dir
```

### 问题 4: Node.js依赖安装失败

**错误信息**:
```
npm ERR! code ELIFECYCLE
```

**解决方案**:
```bash
# 1. 清理缓存
npm cache clean --force

# 2. 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install

# 3. 使用国内镜像（中国用户）
npm install --registry=https://registry.npmmirror.com
```

### 问题 5: 无法登录

**症状**: 输入正确的账号密码仍无法登录

**解决方案**:
```bash
# 1. 检查数据库是否有管理员用户
cd backend
sqlite3 knowledge_platform.db "SELECT * FROM users WHERE email='admin@knowledge-platform.com';"

# 2. 如果没有，手动创建
python create_admin.py

# 3. 重置管理员密码
python -c "
from app.core.security import get_password_hash
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@knowledge-platform.com').first()
if user:
    user.password_hash = get_password_hash('admin123')
    db.commit()
    print('密码已重置为: admin123')
else:
    print('用户不存在')
db.close()
"
```

### 问题 6: 前端无法连接后端

**症状**: 前端显示网络错误

**解决方案**:
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 检查前端API配置
# 编辑 frontend/src/services/api.ts
# 确保 baseURL 正确: http://localhost:8000/api/v1

# 3. 检查CORS配置
# 后端应允许前端域名访问
```

### 问题 7: 数据库文件损坏

**错误信息**:
```
database disk image is malformed
```

**解决方案**:
```bash
# 1. 尝试修复
cd backend
sqlite3 knowledge_platform.db ".recover" | sqlite3 knowledge_platform_recovered.db

# 2. 如果无法修复，从备份恢复
# 或删除并重新初始化（会丢失数据）
rm knowledge_platform.db*
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🔧 高级配置 / Advanced Configuration

### 使用 MySQL 数据库

```bash
# 1. 安装MySQL
# macOS:
brew install mysql
brew services start mysql

# Ubuntu:
sudo apt install mysql-server

# 2. 创建数据库
mysql -u root -p
CREATE DATABASE knowledge_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'kp_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON knowledge_platform.* TO 'kp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 3. 配置环境变量
cd backend
nano .env

# 添加:
DATABASE_TYPE=mysql
DATABASE_URL=mysql+aiomysql://kp_user:your_password@localhost:3306/knowledge_platform

# 4. 安装MySQL驱动
pip install aiomysql pymysql

# 5. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 使用 PostgreSQL 数据库

```bash
# 1. 安装PostgreSQL
# macOS:
brew install postgresql
brew services start postgresql

# Ubuntu:
sudo apt install postgresql postgresql-contrib

# 2. 创建数据库
sudo -u postgres psql
CREATE DATABASE knowledge_platform;
CREATE USER kp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE knowledge_platform TO kp_user;
\q

# 3. 配置环境变量
cd backend
nano .env

# 添加:
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://kp_user:your_password@localhost:5432/knowledge_platform

# 4. 安装PostgreSQL驱动
pip install asyncpg

# 5. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📚 下一步 / Next Steps

部署成功后，您可以：

1. **修改管理员密码** - 登录后在设置页面修改
2. **创建普通用户** - 在用户管理页面添加
3. **导入现有数据** - 使用导入功能
4. **配置备份** - 设置定期备份
5. **阅读文档** - 了解更多功能

### 相关文档

- [快速开始指南](README_QUICKSTART.md)
- [故障排查指南](TROUBLESHOOTING.md)
- [URL导入指南](URL_IMPORT_GUIDE.md)
- [用户管理指南](USER_MANAGEMENT_GUIDE.md)
- [API文档](http://localhost:8000/docs)

---

## 🆘 获取帮助 / Get Help

如果遇到问题：

1. **查看日志**:
   ```bash
   # 后端日志
   tail -f backend/logs/app.log
   
   # 前端控制台
   # 浏览器 F12 → Console
   ```

2. **搜索文档**: 查看 [故障排查指南](TROUBLESHOOTING.md)

3. **GitHub Issues**: https://github.com/jackchen1941/knowledge_platform/issues

4. **社区讨论**: https://github.com/jackchen1941/knowledge_platform/discussions

---

**🎉 恭喜！您已成功部署知识管理平台！**

**📧 默认管理员**: admin@knowledge-platform.com / admin123

**🌐 访问地址**: http://localhost:3000

---

*最后更新: 2026-02-10*
*版本: v1.1.0*
