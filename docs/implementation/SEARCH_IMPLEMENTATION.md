# 搜索功能实现文档

## 概述

本文档描述了知识管理平台的搜索功能实现。当前实现基于数据库的全文搜索，为MVP阶段提供完整的搜索能力。

## 实现的功能

### Task 6.2 - 高级搜索功能 ✅

**文件：**
- `backend/app/services/search.py` - 搜索业务逻辑服务
- `backend/app/schemas/search.py` - 搜索Pydantic schemas
- `backend/app/api/v1/endpoints/search.py` - 搜索REST API端点

**功能特性：**

### 1. 全文搜索
- 在标题、内容、摘要中搜索关键词
- 支持模糊匹配（ILIKE）
- 不区分大小写

### 2. 高级过滤
支持多维度组合过滤：
- **分类过滤**：按category_id筛选
- **标签过滤**：按tag_ids筛选（支持多个标签）
- **可见性**：private/shared/public
- **发布状态**：已发布/草稿
- **来源平台**：CSDN、微信公众号等
- **内容类型**：markdown/html/plain
- **日期范围**：创建时间、更新时间
- **字数范围**：最小/最大字数

### 3. 排序功能
支持按以下字段排序：
- 创建时间（created_at）
- 更新时间（updated_at）
- 标题（title）
- 浏览次数（view_count）
- 字数（word_count）

支持升序（asc）和降序（desc）

### 4. 分页
- 可配置每页数量（1-100）
- 返回总数和总页数
- 支持页码跳转

### 5. 搜索建议
- 基于前缀的自动补全
- 从知识条目、标签、分类中提供建议
- 按类型分类返回

### 6. 相似内容推荐
- 基于标签和分类的相似度
- 查找相关知识条目
- 支持知识发现

### 7. 搜索历史和热门搜索
- 预留接口用于搜索历史记录
- 预留接口用于热门搜索统计
- 需要额外的数据表支持（待实现）

## API端点

### 主搜索端点
```
GET /api/v1/search
```

**查询参数：**
- `q`: 搜索关键词
- `category_id`: 分类ID
- `tag_ids`: 标签ID列表
- `visibility`: 可见性
- `is_published`: 是否已发布
- `source_platform`: 来源平台
- `content_type`: 内容类型
- `created_after`: 创建时间起始
- `created_before`: 创建时间结束
- `updated_after`: 更新时间起始
- `updated_before`: 更新时间结束
- `min_word_count`: 最小字数
- `max_word_count`: 最大字数
- `sort_by`: 排序字段
- `sort_order`: 排序方向
- `page`: 页码
- `page_size`: 每页数量

**响应：**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 搜索建议
```
GET /api/v1/search/suggestions?prefix=python
```

**响应：**
```json
{
  "suggestions": [
    {
      "text": "Python编程基础",
      "type": "knowledge_item",
      "id": "xxx"
    },
    {
      "text": "Python",
      "type": "tag",
      "id": "yyy"
    }
  ]
}
```

### 相似内容
```
GET /api/v1/search/similar/{knowledge_item_id}?limit=10
```

**响应：**
```json
{
  "items": [...],
  "total": 10,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### 搜索历史
```
GET /api/v1/search/history?limit=10
```

### 热门搜索
```
GET /api/v1/search/popular?limit=10
```

## 使用示例

### 基础搜索
```bash
curl -X GET "http://localhost:8000/api/v1/search?q=python" \
  -H "Authorization: Bearer <token>"
```

### 高级搜索
```bash
curl -X GET "http://localhost:8000/api/v1/search?q=python&category_id=xxx&tag_ids=yyy&tag_ids=zzz&is_published=true&sort_by=view_count&sort_order=desc&page=1&page_size=20" \
  -H "Authorization: Bearer <token>"
```

### 日期范围搜索
```bash
curl -X GET "http://localhost:8000/api/v1/search?created_after=2024-01-01T00:00:00&created_before=2024-12-31T23:59:59" \
  -H "Authorization: Bearer <token>"
```

### 字数范围搜索
```bash
curl -X GET "http://localhost:8000/api/v1/search?min_word_count=500&max_word_count=2000" \
  -H "Authorization: Bearer <token>"
```

### 搜索建议
```bash
curl -X GET "http://localhost:8000/api/v1/search/suggestions?prefix=py&limit=10" \
  -H "Authorization: Bearer <token>"
```

### 查找相似内容
```bash
curl -X GET "http://localhost:8000/api/v1/search/similar/xxx?limit=10" \
  -H "Authorization: Bearer <token>"
```

## 技术实现

### 数据库查询优化
1. **索引使用**：
   - title、content字段建议添加全文索引
   - category_id、author_id等外键已有索引
   - created_at、updated_at时间字段已有索引

2. **关系预加载**：
   - 使用selectinload预加载tags、category、attachments
   - 避免N+1查询问题

3. **分页优化**：
   - 先计算总数，再获取分页数据
   - 使用offset和limit实现分页

### 搜索性能
- 当前实现使用ILIKE进行模糊搜索
- 对于大数据量，建议：
  - 添加全文索引（PostgreSQL的GIN索引）
  - 考虑集成Elasticsearch（Task 6.1）
  - 使用缓存减少重复查询

### 相似度算法
当前使用简单的基于标签和分类的相似度：
1. 优先返回同分类的内容
2. 其次返回有共同标签的内容
3. 未来可以考虑：
   - TF-IDF文本相似度
   - 向量嵌入（embeddings）
   - 协同过滤

## 安全特性

1. **权限控制**
   - 所有搜索需要JWT认证
   - 只能搜索自己的知识条目
   - 不返回已删除的内容

2. **输入验证**
   - 参数类型和范围验证
   - 日期格式验证
   - 分页限制（最大100条/页）

3. **SQL注入防护**
   - 使用SQLAlchemy ORM
   - 参数化查询
   - 不直接拼接SQL

## 未来改进

### Task 6.1 - Elasticsearch集成
- 更强大的全文搜索
- 更好的性能和扩展性
- 支持中文分词
- 高亮显示搜索结果
- 搜索结果排序优化

### 其他改进
1. **搜索历史**：
   - 创建search_history表
   - 记录用户搜索行为
   - 提供个性化建议

2. **搜索分析**：
   - 统计热门搜索词
   - 分析搜索趋势
   - 优化搜索体验

3. **智能推荐**：
   - 基于用户行为的推荐
   - 机器学习模型
   - 个性化内容发现

4. **语义搜索**：
   - 理解搜索意图
   - 同义词扩展
   - 自然语言查询

## 下一步

- Task 8: 外部平台导入系统
- Task 9: 导出和备份系统
- Task 10: 知识图谱功能

## 注意事项

1. 搜索性能取决于数据量，建议定期优化数据库
2. 对于大量数据，考虑使用Elasticsearch
3. 搜索历史和热门搜索需要额外的表结构
4. 相似度算法可以根据实际需求调整
