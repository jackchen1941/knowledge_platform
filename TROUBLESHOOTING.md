# 🔧 故障排查指南 / Troubleshooting Guide

> 本指南帮助您快速诊断和解决常见问题

## 📋 目录 / Table of Contents

- [快速诊断](#快速诊断)
- [数据库问题](#数据库问题)
- [服务启动问题](#服务启动问题)
- [登录认证问题](#登录认证问题)
- [功能异常问题](#功能异常问题)
- [性能问题](#性能问题)
- [日志分析](#日志分析)

---

## 🚀 快速诊断 / Quick Diagnosis

### 一键健康检查

```bash
# 运行健康检查脚本
./health-check.sh

# 或手动检查
echo "=== 后端服务检查 ==="
curl -s http://localhost:8000/health | jq

echo "=== 前端服务检查 ==="
curl -s http://localhost:3000 > /dev/null && echo "✅ 前端正常" || echo "❌ 前端异常"

echo "=== 数据库检查 ==="
cd backend && ls -lh knowledge_platform.db && cd ..

echo "=== 进程检查 ==="
ps aux | grep -E "uvicorn|node" | grep -v grep
```

### 常见症状快速索引

| 症状 | 可能原因 | 快速解决 |
|------|---------|---------|
| 无法访问前端 | 端口占用/服务未启动 | [查看](#前端无法访问) |
| 无法访问后端 | 端口占用/服务未启动 | [查看](#后端无法访问) |
| 登录失败 | 密码错误/数据库问题 | [查看](#无法登录) |
| 数据库错误 | 文件损坏/权限问题 | [查看](#数据库初始化失败) |
| 导入失败 | 网络问题/格式错误 | [查看](#url导入失败) |
| 页面空白 | 前端构建问题 | [查看](#前端页面空白) |

---

## 🗄️ 数据库问题 / Database Issues

### 问题 1: 数据库初始化失败

**症状**:
```
ERROR: Database initialization failed
ERROR: Could not create tables
```

**诊断步骤**:
```bash
# 1. 检查数据库文件
cd backend
ls -lh knowledge_platform.db

# 2. 检查权限
ls -l knowledge_platform.db

# 3. 检查日志
tail -50 logs/app.log | grep -i "database\|error"
```

**解决方案**:

**方案 A: 重新初始化**
```bash
cd backend

# 1. 备份现有数据库（如果有重要数据）
cp knowledge_platform.db knowledge_platform.db.backup

# 2. 删除数据库文件
rm -f knowledge_platform.db knowledge_platform.db-shm knowledge_platform.db-wal

# 3. 手动初始化
python -c "from app.core.database_init import initialize_database_sync; initialize_database_sync()"

# 4. 验证
sqlite3 knowledge_platform.db ".tables"
# 应显示所有表名
```

**方案 B: 修复权限**
```bash
cd backend

# 修改文件权限
chmod 644 knowledge_platform.db
chmod 755 .

# 修改所有者（如果需要）
chown $USER:$USER knowledge_platform.db
```

**方案 C: 检查磁盘空间**
```bash
# 检查磁盘空间
df -h .

# 如果空间不足，清理临时文件
rm -rf __pycache__
rm -rf .pytest_cache
rm -f *.pyc
```

### 问题 2: 数据库文件损坏

**症状**:
```
database disk image is malformed
database or disk is full
```

**诊断步骤**:
```bash
cd backend

# 1. 检查数据库完整性
sqlite3 knowledge_platform.db "PRAGMA integrity_check;"

# 2. 检查文件大小
ls -lh knowledge_platform.db
```

**解决方案**:

**方案 A: 尝试修复**
```bash
cd backend

# 1. 导出数据
sqlite3 knowledge_platform.db ".dump" > backup.sql

# 2. 创建新数据库
rm knowledge_platform.db
sqlite3 knowledge_platform.db < backup.sql

# 3. 验证
sqlite3 knowledge_platform.db "PRAGMA integrity_check;"
```

**方案 B: 使用恢复工具**
```bash
cd backend

# 使用SQLite恢复命令
sqlite3 knowledge_platform.db ".recover" | sqlite3 knowledge_platform_recovered.db

# 替换原数据库
mv knowledge_platform.db knowledge_platform.db.corrupted
mv knowledge_platform_recovered.db knowledge_platform.db
```

**方案 C: 从备份恢复**
```bash
cd backend

# 如果有备份文件
cp /path/to/backup/knowledge_platform.db .

# 或使用系统备份功能恢复
```

### 问题 3: 数据库连接失败

**症状**:
```
Could not connect to database
Connection refused
```

**诊断步骤**:
```bash
# 1. 检查数据库类型
cd backend
grep DATABASE_TYPE .env

# 2. 对于MySQL/PostgreSQL，检查服务状态
# MySQL:
systemctl status mysql
# 或
brew services list | grep mysql

# PostgreSQL:
systemctl status postgresql
# 或
brew services list | grep postgresql

# 3. 测试连接
# MySQL:
mysql -u root -p -e "SELECT 1;"

# PostgreSQL:
psql -U postgres -c "SELECT 1;"
```

**解决方案**:

**SQLite**:
```bash
# SQLite不需要服务，检查文件路径
cd backend
python -c "
from app.core.config import settings
print(f'Database URL: {settings.DATABASE_URL}')
"
```

**MySQL**:
```bash
# 1. 启动MySQL服务
# macOS:
brew services start mysql

# Ubuntu:
sudo systemctl start mysql

# 2. 检查配置
cd backend
cat .env | grep DATABASE

# 3. 测试连接
mysql -h localhost -u kp_user -p knowledge_platform
```

**PostgreSQL**:
```bash
# 1. 启动PostgreSQL服务
# macOS:
brew services start postgresql

# Ubuntu:
sudo systemctl start postgresql

# 2. 检查配置
cd backend
cat .env | grep DATABASE

# 3. 测试连接
psql -h localhost -U kp_user -d knowledge_platform
```

### 问题 4: 数据库迁移失败

**症状**:
```
Migration failed
Alembic error
```

**解决方案**:
```bash
cd backend

# 1. 检查迁移状态
alembic current

# 2. 查看迁移历史
alembic history

# 3. 重置迁移
alembic downgrade base
alembic upgrade head

# 4. 如果仍然失败，重新初始化
rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## 🚀 服务启动问题 / Service Startup Issues

### 问题 1: 后端无法启动

**症状**:
```
Error: Address already in use
ModuleNotFoundError
ImportError
```

**诊断步骤**:
```bash
# 1. 检查端口占用
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 2. 检查Python环境
cd backend
which python
python --version

# 3. 检查依赖
pip list | grep fastapi
pip list | grep sqlalchemy

# 4. 检查日志
tail -50 logs/app.log
```

**解决方案**:

**端口被占用**:
```bash
# 方案A: 杀死占用进程
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
# 找到PID后
taskkill /PID <pid> /F

# 方案B: 使用其他端口
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**依赖问题**:
```bash
cd backend

# 1. 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 2. 如果仍有问题，重建虚拟环境
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**模块导入错误**:
```bash
cd backend

# 1. 检查PYTHONPATH
echo $PYTHONPATH

# 2. 设置PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 3. 或使用python -m运行
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 问题 2: 前端无法启动

**症状**:
```
Error: EADDRINUSE
Module not found
npm ERR!
```

**诊断步骤**:
```bash
# 1. 检查端口占用
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# 2. 检查Node版本
node --version
npm --version

# 3. 检查依赖
cd frontend
ls node_modules | wc -l
```

**解决方案**:

**端口被占用**:
```bash
# 方案A: 杀死占用进程
lsof -ti:3000 | xargs kill -9

# 方案B: 使用其他端口
PORT=3001 npm start
```

**依赖问题**:
```bash
cd frontend

# 1. 清理并重新安装
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# 2. 如果仍有问题，使用yarn
npm install -g yarn
yarn install
yarn start
```

**内存不足**:
```bash
cd frontend

# 增加Node内存限制
export NODE_OPTIONS="--max-old-space-size=4096"
npm start
```

### 问题 3: 服务启动后立即崩溃

**诊断步骤**:
```bash
# 1. 查看完整错误信息
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1 | tee startup.log

# 2. 检查配置文件
cat .env

# 3. 检查日志
tail -100 logs/app.log
tail -100 logs/errors.log
```

**常见原因和解决方案**:

**配置错误**:
```bash
# 检查.env文件格式
cd backend
cat .env

# 确保没有多余空格和引号
# 错误: DATABASE_URL = "sqlite:///./db.db"
# 正确: DATABASE_URL=sqlite:///./db.db
```

**权限问题**:
```bash
# 检查日志目录权限
cd backend
ls -ld logs/
chmod 755 logs/
chmod 644 logs/*.log
```

---

## 🔐 登录认证问题 / Authentication Issues

### 问题 1: 无法登录

**症状**:
- 输入正确密码仍提示错误
- 登录后立即退出
- Token无效

**诊断步骤**:
```bash
# 1. 检查用户是否存在
cd backend
sqlite3 knowledge_platform.db "SELECT id, email, username, is_active FROM users WHERE email='admin@knowledge-platform.com';"

# 2. 测试登录API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@knowledge-platform.com","password":"admin123"}' \
  -v

# 3. 检查JWT配置
grep SECRET_KEY backend/.env
```

**解决方案**:

**重置管理员密码**:
```bash
cd backend

# 方式1: 使用脚本
python create_admin.py

# 方式2: 使用Python命令
python << EOF
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@knowledge-platform.com').first()
if user:
    user.password_hash = get_password_hash('admin123')
    db.commit()
    print('✅ 密码已重置为: admin123')
else:
    print('❌ 用户不存在')
db.close()
EOF
```

**创建新管理员**:
```bash
cd backend

python << EOF
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
import uuid

db = SessionLocal()

# 创建新管理员
new_admin = User(
    id=str(uuid.uuid4()),
    email='newadmin@example.com',
    username='newadmin',
    full_name='New Administrator',
    password_hash=get_password_hash('newpassword123'),
    is_active=True,
    is_superuser=True,
    is_verified=True
)

db.add(new_admin)
db.commit()
print('✅ 新管理员创建成功')
print('邮箱: newadmin@example.com')
print('密码: newpassword123')
db.close()
EOF
```

**检查Token配置**:
```bash
cd backend

# 1. 确保SECRET_KEY存在
if ! grep -q "SECRET_KEY" .env; then
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "✅ SECRET_KEY已生成"
fi

# 2. 重启后端服务
```

### 问题 2: Token过期太快

**解决方案**:
```bash
cd backend

# 编辑.env文件
nano .env

# 添加或修改
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时
REFRESH_TOKEN_EXPIRE_DAYS=30      # 30天

# 重启服务
```

### 问题 3: CORS错误

**症状**:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解决方案**:
```bash
cd backend

# 检查CORS配置
grep -A 5 "CORSMiddleware" app/main.py

# 如果需要，添加前端域名
# 编辑 app/main.py
# allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
```

---

## 🐛 功能异常问题 / Feature Issues

### 问题 1: URL导入失败

**症状**:
```
Could not fetch content from URL
Import failed
```

**诊断步骤**:
```bash
# 1. 测试URL是否可访问
curl -I "https://blog.csdn.net/xxx/article/details/xxx"

# 2. 检查网络连接
ping blog.csdn.net

# 3. 测试导入API
cd backend
python << EOF
from app.services.adapters.url_adapter import URLAdapter
import asyncio

async def test():
    adapter = URLAdapter()
    result = await adapter.import_from_url("https://blog.csdn.net/xxx/article/details/xxx")
    print(result)

asyncio.run(test())
EOF
```

**解决方案**:

**网络问题**:
```bash
# 1. 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 2. 如果需要代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# 3. 重启后端服务
```

**反爬虫限制**:
```python
# 编辑 backend/app/services/adapters/url_adapter.py
# 增加请求头或延迟

headers = {
    'User-Agent': 'Mozilla/5.0 ...',
    'Referer': 'https://www.google.com/',
    # 添加更多headers
}

# 添加延迟
import time
time.sleep(2)
```

### 问题 2: 搜索功能不工作

**诊断步骤**:
```bash
# 1. 测试搜索API
curl "http://localhost:8000/api/v1/search?q=test"

# 2. 检查数据库
cd backend
sqlite3 knowledge_platform.db "SELECT COUNT(*) FROM knowledge_items;"
```

**解决方案**:
```bash
# 如果没有数据，创建测试数据
cd backend
python << EOF
from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeItem
import uuid

db = SessionLocal()

# 创建测试知识
test_item = KnowledgeItem(
    id=str(uuid.uuid4()),
    title="测试知识",
    content="这是一个测试知识条目",
    author_id="admin-user-id"  # 替换为实际用户ID
)

db.add(test_item)
db.commit()
print('✅ 测试数据创建成功')
db.close()
EOF
```

### 问题 3: 文件上传失败

**症状**:
```
File too large
Upload failed
```

**解决方案**:
```bash
cd backend

# 1. 检查上传限制
grep MAX_UPLOAD_SIZE .env

# 2. 增加限制（如果需要）
echo "MAX_UPLOAD_SIZE=52428800" >> .env  # 50MB

# 3. 检查磁盘空间
df -h .

# 4. 检查上传目录权限
ls -ld uploads/
chmod 755 uploads/
```

---

## ⚡ 性能问题 / Performance Issues

### 问题 1: 响应速度慢

**诊断步骤**:
```bash
# 1. 测试API响应时间
time curl http://localhost:8000/api/v1/knowledge

# 2. 检查数据库大小
cd backend
ls -lh knowledge_platform.db

# 3. 检查系统资源
top  # 或 htop
```

**解决方案**:

**优化数据库**:
```bash
cd backend

# SQLite优化
sqlite3 knowledge_platform.db << EOF
PRAGMA optimize;
VACUUM;
ANALYZE;
EOF

# 检查索引
sqlite3 knowledge_platform.db ".schema" | grep INDEX
```

**增加缓存**:
```bash
# 安装Redis（可选）
# macOS:
brew install redis
brew services start redis

# Ubuntu:
sudo apt install redis-server
sudo systemctl start redis

# 配置后端使用Redis
cd backend
echo "REDIS_URL=redis://localhost:6379" >> .env
```

### 问题 2: 内存占用高

**诊断步骤**:
```bash
# 检查进程内存
ps aux | grep -E "uvicorn|node" | awk '{print $4, $11}'

# 详细内存分析
# macOS:
vmmap <pid>

# Linux:
pmap <pid>
```

**解决方案**:
```bash
# 1. 限制worker数量
cd backend
uvicorn app.main:app --workers 2 --host 0.0.0.0 --port 8000

# 2. 前端生产构建
cd frontend
npm run build
# 使用nginx或其他服务器提供静态文件
```

---

## 📊 日志分析 / Log Analysis

### 查看日志

```bash
# 后端日志
cd backend

# 应用日志
tail -f logs/app.log

# 错误日志
tail -f logs/errors.log

# 安全日志
tail -f logs/security.log

# 搜索特定错误
grep -i "error\|exception\|failed" logs/app.log | tail -20

# 按时间过滤
grep "2026-02-10" logs/app.log
```

### 日志级别

```bash
# 修改日志级别
cd backend
nano .env

# 添加
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 重启服务
```

### 常见错误模式

| 错误信息 | 含义 | 解决方案 |
|---------|------|---------|
| `Connection refused` | 服务未启动 | 启动服务 |
| `Permission denied` | 权限不足 | 修改权限 |
| `No such file` | 文件不存在 | 检查路径 |
| `Timeout` | 超时 | 检查网络/增加超时 |
| `Out of memory` | 内存不足 | 增加内存/优化代码 |

---

## 🆘 获取更多帮助 / Get More Help

### 1. 收集诊断信息

```bash
# 运行诊断脚本
./diagnose.sh > diagnosis.txt

# 或手动收集
cat > diagnosis.txt << EOF
=== 系统信息 ===
$(uname -a)
$(python --version)
$(node --version)

=== 服务状态 ===
$(curl -s http://localhost:8000/health)
$(curl -s http://localhost:3000 > /dev/null && echo "Frontend: OK" || echo "Frontend: Failed")

=== 数据库信息 ===
$(ls -lh backend/knowledge_platform.db)

=== 最近错误 ===
$(tail -50 backend/logs/errors.log)
EOF
```

### 2. 提交Issue

访问: https://github.com/jackchen1941/knowledge_platform/issues

包含以下信息:
- 操作系统和版本
- Python和Node.js版本
- 错误信息和日志
- 复现步骤
- 诊断信息文件

### 3. 社区讨论

访问: https://github.com/jackchen1941/knowledge_platform/discussions

---

**💡 提示**: 大多数问题都可以通过查看日志和重新初始化数据库解决。

---

*最后更新: 2026-02-10*
*版本: v1.1.0*
