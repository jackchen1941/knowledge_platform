# 开发指南

## 环境设置

### 系统要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选)

### 本地开发环境

1. **克隆项目**
```bash
git clone <repository-url>
cd knowledge-management-platform
```

2. **安装依赖**
```bash
make install
```

3. **启动开发服务器**
```bash
make dev
```

## 项目结构

```
knowledge-management-platform/
├── backend/                 # Python FastAPI 后端
│   ├── app/                # 应用代码
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   └── services/       # 业务逻辑
│   ├── tests/              # 测试代码
│   ├── alembic/            # 数据库迁移
│   └── requirements.txt    # Python依赖
├── frontend/               # React 前端
│   ├── src/                # 源代码
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面组件
│   │   ├── store/          # Redux状态管理
│   │   ├── services/       # API服务
│   │   └── types/          # TypeScript类型
│   └── package.json        # Node.js依赖
└── docker-compose.yml      # Docker编排
```

## 开发规范

### 后端开发

#### 代码风格
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 flake8 进行代码检查
- 使用 mypy 进行类型检查

#### 安全最佳实践
1. **输入验证**: 所有用户输入必须经过验证和清理
2. **SQL注入防护**: 使用ORM参数化查询
3. **XSS防护**: 对输出进行HTML编码
4. **CSRF防护**: 使用CSRF令牌
5. **认证**: 使用JWT令牌和安全的密码哈希
6. **权限控制**: 实施基于角色的访问控制
7. **审计日志**: 记录所有安全相关事件

#### 数据库操作
```python
# 正确的方式 - 使用ORM
user = await session.execute(
    select(User).where(User.email == email)
)

# 错误的方式 - 容易SQL注入
# query = f"SELECT * FROM users WHERE email = '{email}'"
```

#### API设计
- 使用RESTful设计原则
- 实施适当的HTTP状态码
- 提供清晰的错误消息
- 使用Pydantic进行数据验证

### 前端开发

#### 代码风格
- 使用 Prettier 进行代码格式化
- 使用 ESLint 进行代码检查
- 使用 TypeScript 进行类型检查

#### 组件设计
- 使用函数组件和Hooks
- 实施适当的错误边界
- 使用React.memo进行性能优化
- 遵循单一职责原则

#### 状态管理
- 使用Redux Toolkit进行全局状态管理
- 使用React Query进行服务器状态管理
- 避免不必要的重新渲染

## 测试策略

### 后端测试
```bash
# 运行所有测试
make test-backend

# 运行特定测试
cd backend && pytest tests/test_auth.py -v

# 运行覆盖率测试
cd backend && pytest --cov=app --cov-report=html
```

### 前端测试
```bash
# 运行所有测试
make test-frontend

# 运行特定测试
cd frontend && npm test -- --testNamePattern="LoginPage"
```

### 属性测试
使用Hypothesis进行属性测试：
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_sanitize_string_length(text):
    result = InputSanitizer.sanitize_string(text)
    assert len(result) <= len(text)
```

## 部署

### 开发环境
```bash
make dev
```

### 生产环境
```bash
make deploy-prod
```

### Docker部署
```bash
make docker-build
make docker-up
```

## 安全检查

定期运行安全检查：
```bash
make security-check
```

## 性能优化

### 后端优化
- 使用数据库索引
- 实施查询优化
- 使用Redis缓存
- 异步处理长时间任务

### 前端优化
- 代码分割和懒加载
- 图片优化和压缩
- 使用CDN
- 实施缓存策略

## 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查数据库URL配置
   - 确保数据库服务正在运行

2. **CORS错误**
   - 检查CORS_ORIGINS配置
   - 确保前端URL在允许列表中

3. **认证失败**
   - 检查JWT密钥配置
   - 验证令牌有效期设置

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 运行测试
5. 创建Pull Request

### 提交消息格式
```
type(scope): description

feat(auth): add password reset functionality
fix(api): resolve CORS issue
docs(readme): update installation instructions
```