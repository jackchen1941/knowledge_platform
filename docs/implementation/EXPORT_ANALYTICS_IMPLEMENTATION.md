# 导出和统计功能实现文档

## 概述

本文档描述了知识管理平台的导出和统计分析功能实现。

---

## Task 9.1 - 导出功能 ✅

### 实现的文件
- `backend/app/services/export.py` - 导出业务逻辑
- `backend/app/schemas/export.py` - 导出schemas
- `backend/app/api/v1/endpoints/import_export.py` - 导出API端点

### 功能特性

#### 1. 单个导出
支持将单个知识条目导出为：
- **Markdown格式** (.md)
  - 包含标题、元数据、摘要、正文、附件列表
  - 可选包含/排除元数据
  - 适合文本编辑器和版本控制

- **JSON格式** (.json)
  - 完整的结构化数据
  - 包含所有字段和关系
  - 可选包含版本历史
  - 适合数据迁移和备份

- **HTML格式** (.html)
  - 美观的网页格式
  - 内置CSS样式
  - 支持Markdown转HTML
  - 适合分享和打印

#### 2. 批量导出
- 导出多个知识条目到ZIP文件
- 支持所有格式（Markdown/JSON/HTML）
- 自动生成安全的文件名
- 失败项不影响其他项导出

#### 3. 全量导出
- 导出用户的所有知识条目
- 可选包含已删除的项
- 打包为ZIP文件
- 适合完整备份

### API端点

#### 导出单个条目
```
POST /api/v1/import-export/export/{knowledge_item_id}
```

**请求体：**
```json
{
  "format": "markdown",
  "include_metadata": true,
  "include_versions": false
}
```

**响应：** 直接返回文件内容

#### 批量导出
```
POST /api/v1/import-export/export/batch
```

**请求体：**
```json
{
  "item_ids": ["id1", "id2", "id3"],
  "format": "markdown",
  "include_metadata": true
}
```

**响应：** ZIP文件

#### 全量导出
```
POST /api/v1/import-export/export/all
```

**请求体：**
```json
{
  "format": "json",
  "include_deleted": false
}
```

**响应：** ZIP文件

### 使用示例

#### 导出为Markdown
```bash
curl -X POST "http://localhost:8000/api/v1/import-export/export/xxx" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"format": "markdown", "include_metadata": true}' \
  --output article.md
```

#### 批量导出
```bash
curl -X POST "http://localhost:8000/api/v1/import-export/export/batch" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"item_ids": ["id1", "id2"], "format": "json"}' \
  --output export.zip
```

#### 全量导出
```bash
curl -X POST "http://localhost:8000/api/v1/import-export/export/all" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"format": "markdown", "include_deleted": false}' \
  --output full_backup.zip
```

---

## Task 11.1 - 统计分析功能 ✅

### 实现的文件
- `backend/app/services/analytics.py` - 统计分析业务逻辑
- `backend/app/schemas/analytics.py` - 统计schemas
- `backend/app/api/v1/endpoints/analytics.py` - 统计API端点

### 功能特性

#### 1. 概览统计
提供用户的整体数据概览：
- 总条目数、已发布数、草稿数、已删除数
- 总字数、总浏览量
- 标签数、分类数
- 平均每篇字数

#### 2. 近期活动
分析指定时间段内的活动：
- 创建的条目数
- 更新的条目数
- 发布的条目数
- 总活跃度

#### 3. 内容分布
多维度的内容分布统计：
- **按分类分布**：各分类的条目数量（Top 10）
- **按内容类型分布**：Markdown/HTML/Plain
- **按可见性分布**：私有/共享/公开

#### 4. 热门标签
- 按使用次数排序的标签列表
- 显示标签颜色和使用次数
- 可配置返回数量

#### 5. 写作趋势
时间序列分析：
- 每日创建的条目数
- 每日写作字数
- 平均每天创建条目数
- 平均每天写作字数

#### 6. 字数分布
按字数范围统计条目分布：
- 短文 (0-500字)
- 中等 (501-1000字)
- 长文 (1001-2000字)
- 很长 (2001-5000字)
- 超长 (5000字以上)

#### 7. 来源平台统计
统计从各平台导入的内容数量：
- 原创内容
- CSDN、微信公众号等外部平台
- 按数量排序

### API端点

#### 概览统计
```
GET /api/v1/analytics/overview
```

**响应：**
```json
{
  "total_items": 100,
  "published_items": 80,
  "draft_items": 20,
  "deleted_items": 5,
  "total_words": 50000,
  "total_views": 1000,
  "total_tags": 30,
  "total_categories": 10,
  "average_words_per_item": 500
}
```

#### 近期活动
```
GET /api/v1/analytics/activity?days=30
```

#### 内容分布
```
GET /api/v1/analytics/distribution
```

#### 热门标签
```
GET /api/v1/analytics/tags/top?limit=10
```

#### 写作趋势
```
GET /api/v1/analytics/trends?days=30
```

**响应：**
```json
{
  "period_days": 30,
  "daily_stats": [
    {
      "date": "2024-01-01",
      "items_created": 3,
      "words_written": 1500
    }
  ],
  "total_items": 45,
  "total_words": 22500,
  "average_items_per_day": 1.5,
  "average_words_per_day": 750
}
```

#### 字数分布
```
GET /api/v1/analytics/word-count
```

#### 来源平台统计
```
GET /api/v1/analytics/sources
```

### 使用示例

#### 获取概览统计
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/overview" \
  -H "Authorization: Bearer <token>"
```

#### 获取30天写作趋势
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/trends?days=30" \
  -H "Authorization: Bearer <token>"
```

#### 获取热门标签
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/tags/top?limit=20" \
  -H "Authorization: Bearer <token>"
```

---

## 技术实现

### 导出功能

#### Markdown导出
- 标准Markdown格式
- 前置元数据（YAML风格）
- 清晰的章节结构
- 附件链接列表

#### JSON导出
- 完整的数据结构
- 包含所有关系（标签、分类、附件）
- 可选版本历史
- 易于解析和导入

#### HTML导出
- 响应式设计
- 内联CSS样式
- Markdown自动转换
- 适合打印的布局

#### ZIP打包
- 使用Python zipfile模块
- 内存中创建（BytesIO）
- 自动文件名清理
- 错误容错处理

### 统计分析

#### 数据聚合
- 使用SQLAlchemy的聚合函数
- COUNT、SUM、AVG等
- GROUP BY分组统计
- 高效的数据库查询

#### 时间序列
- 按日期分组
- 时间范围过滤
- 趋势计算

#### 性能优化
- 单次查询获取多个统计
- 避免N+1查询
- 使用数据库索引
- 结果可缓存

---

## 安全特性

1. **权限控制**
   - 所有操作需要JWT认证
   - 只能导出/统计自己的数据
   - 文件名安全处理

2. **数据验证**
   - 格式验证
   - 参数范围检查
   - 错误处理

3. **资源保护**
   - 批量操作限制
   - 文件大小控制
   - 超时保护

---

## 未来改进

### 导出功能
1. **PDF导出**
   - 使用WeasyPrint或ReportLab
   - 自定义模板
   - 目录和页码

2. **Word导出**
   - 使用python-docx
   - 格式保留
   - 图片嵌入

3. **定时导出**
   - 自动备份
   - 邮件发送
   - 云存储同步

### 统计分析
1. **高级图表**
   - 更多可视化类型
   - 交互式图表
   - 导出图表

2. **自定义报告**
   - 用户自定义指标
   - 报告模板
   - 定期报告

3. **预测分析**
   - 写作习惯预测
   - 内容推荐
   - 目标跟踪

---

## 下一步

- Task 10: 知识图谱功能
- Task 14: React前端开发
- Task 9.2: 数据备份和恢复

---

**当前状态**: 导出和基础统计功能已完成，可以导出多种格式并查看详细的统计数据。
