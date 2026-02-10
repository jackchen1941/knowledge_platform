# 测试文档 / Testing Documentation

本目录包含项目的所有测试文件。

## 目录结构

```
tests/
├── api/                          # API集成测试
│   ├── test_knowledge_graph_api.py   # 知识图谱API测试
│   ├── test_user_management_api.py   # 用户管理API测试
│   └── run_all_api_tests.py          # 运行所有API测试
├── features/                     # 功能测试
│   ├── test_auth.py
│   ├── test_knowledge_simple.py
│   └── ...
├── integration/                  # 集成测试
│   ├── test_all_features.py
│   └── ...
├── security/                     # 安全测试
│   └── test_security_comprehensive.py
└── system/                       # 系统测试
    ├── test_system.py
    └── ...
```

## 运行测试

### 运行所有API测试
```bash
python tests/api/run_all_api_tests.py
```

### 运行单个API测试
```bash
# 知识图谱API测试
python tests/api/test_knowledge_graph_api.py

# 用户管理API测试
python tests/api/test_user_management_api.py
```

### 运行后端单元测试
```bash
cd backend
pytest
```

## API测试说明

### 知识图谱API测试 (test_knowledge_graph_api.py)
测试知识图谱相关的所有API端点：
- 创建知识链接
- 获取知识链接（outgoing/incoming/both）
- 删除知识链接
- 获取相关知识推荐
- 获取图谱统计

### 用户管理API测试 (test_user_management_api.py)
测试用户管理相关的所有API端点：
- 获取用户列表
- 获取用户详情
- 创建用户
- 更新用户
- 删除用户
- 获取用户统计

## 测试要求

### 前置条件
1. 后端服务运行在 `http://localhost:8000`
2. 管理员账户: `admin@admin.com` / `admin12345`
3. 数据库已初始化

### 测试特点
- ✅ 自动化测试
- ✅ 详细输出
- ✅ 自动清理测试数据
- ✅ 可重复运行
- ✅ 独立运行

## 添加新测试

### 1. 创建测试文件
在 `tests/api/` 目录下创建新的测试文件：
```bash
touch tests/api/test_new_feature_api.py
```

### 2. 使用测试模板
```python
#!/usr/bin/env python3
"""
新功能API测试
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@admin.com"
PASSWORD = "admin12345"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def main():
    print("="*60)
    print("新功能API测试")
    print("="*60)
    
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    # 添加测试逻辑
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()
```

### 3. 运行测试
```bash
python tests/api/run_all_api_tests.py
```

## 最佳实践

1. **测试独立性**: 每个测试应该独立运行，不依赖其他测试
2. **数据清理**: 测试结束后清理创建的测试数据
3. **详细输出**: 提供清晰的测试输出和状态信息
4. **错误处理**: 妥善处理API错误和异常情况
5. **可重复性**: 测试应该可以多次运行得到相同结果

## 持续集成

这些测试可以集成到CI/CD流程中：

```yaml
# .github/workflows/api-tests.yml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run API Tests
        run: python tests/api/run_all_api_tests.py
```

## 相关文档

- [知识图谱测试结果](../KNOWLEDGE_GRAPH_TEST_RESULTS.md)
- [用户管理API修复](../USER_MANAGEMENT_API_FIX.md)
- [错误处理修复](../ERROR_HANDLING_FIX.md)
