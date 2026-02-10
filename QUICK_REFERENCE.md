# 知识管理平台 - 快速参考

## 🚀 快速启动

### 服务地址
- **前端**: http://localhost:3000
- **后端**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 登录信息
```
邮箱: admin@admin.com
密码: admin12345
```

---

## 📝 URL导入（最常用功能）

### 前端操作
1. 访问 http://localhost:3000
2. 登录
3. 点击左侧菜单"导入管理"
4. 选择"URL快速导入"标签页
5. 输入URL → 点击"立即导入"

### API调用
```bash
# 单个URL导入
curl -X POST "http://localhost:8000/api/v1/import-adapters/import-url?url=https://example.com/article&category=技术文章&tags=Python" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 批量URL导入
curl -X POST "http://localhost:8000/api/v1/import-adapters/import-urls" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["url1", "url2"],
    "category": "技术文章",
    "tags": ["Python"]
  }'
```

---

## 🔄 多设备同步

### 注册设备
```bash
POST /api/v1/sync/devices/register
{
  "device_name": "我的iPhone",
  "device_type": "mobile",
  "device_id": "unique-id"
}
```

### 拉取更新
```bash
POST /api/v1/sync/pull
{
  "device_id": "device-uuid"
}
```

### 推送更新
```bash
POST /api/v1/sync/push
{
  "device_id": "device-uuid",
  "changes": [...]
}
```

---

## 📚 支持的URL类型

| 平台 | 示例URL |
|------|---------|
| GitHub | `https://github.com/user/repo/blob/main/README.md` |
| CSDN | `https://blog.csdn.net/user/article/details/123456` |
| 知乎 | `https://zhuanlan.zhihu.com/p/123456789` |
| 掘金 | `https://juejin.cn/post/7123456789012345678` |
| 简书 | `https://www.jianshu.com/p/abc123def456` |
| Medium | `https://medium.com/@user/article-title` |

---

## 🧪 测试脚本

```bash
# 综合测试
python comprehensive_test.py

# URL导入测试
python test_url_import.py

# 详细测试
python test_url_import_detailed.py

# 演示脚本
python demo_url_import.py
```

---

## 📖 文档索引

| 文档 | 用途 |
|------|------|
| `URL_IMPORT_GUIDE.md` | URL导入详细指南 |
| `MULTI_DEVICE_AND_IMPORT_GUIDE.md` | 多设备同步和导入完整指南 |
| `FEATURES_SUMMARY.md` | 功能总结 |
| `FINAL_STATUS_REPORT.md` | 最终状态报告 |
| `README.md` | 项目概述 |

---

## 🔧 常用命令

### 启动服务
```bash
# 后端
./start-backend.sh

# 前端
cd frontend && npm start
```

### 查看日志
```bash
# 应用日志
tail -f backend/logs/app.log

# 错误日志
tail -f backend/logs/errors.log
```

### 数据库操作
```bash
# 进入Python环境
source knowledge_platform_env/bin/activate
python

# 查询数据
from app.core.database import get_db
# ...
```

---

## 💡 快速技巧

### 1. 快速导入文章
```
复制URL → 前端粘贴 → 点击导入 → 完成
```

### 2. 批量导入
```
准备URL列表 → 批量导入 → 统一设置分类标签
```

### 3. 多设备同步
```
注册设备 → 自动同步 → 所有设备数据一致
```

---

## 🐛 故障排除

### 问题: 导入失败
```bash
# 检查后端日志
tail -f backend/logs/app.log

# 检查URL是否可访问
curl -I https://example.com/article
```

### 问题: 前端无法访问
```bash
# 检查前端进程
ps aux | grep "npm start"

# 重启前端
cd frontend && npm start
```

### 问题: 后端无法访问
```bash
# 检查后端进程
ps aux | grep uvicorn

# 重启后端
./start-backend.sh
```

---

## 📞 获取帮助

1. 查看API文档: http://localhost:8000/docs
2. 查看详细文档: `URL_IMPORT_GUIDE.md`
3. 查看日志: `backend/logs/app.log`
4. 运行测试验证: `python test_url_import.py`

---

**提示**: 将此文档加入书签，随时查阅！
