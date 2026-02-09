# 知识图谱和备份功能实现文档

## 概述

本文档描述了知识图谱和数据备份功能的实现。

---

## Task 10.1 - 知识关联系统 ✅

### 实现的文件
- `backend/app/services/knowledge_graph.py` - 知识图谱服务
- `backend/app/schemas/knowledge_graph.py` - 知识图谱schemas
- `backend/app/api/v1/endpoints/knowledge_graph.py` - 知识图谱API

### 功能特性

#### 1. 知识链接管理
- **创建链接** - 在两个知识条目之间建立关联
- **删除链接** - 移除知识关联
- **查询链接** - 获取某个知识的所有关联
  - 支持方向筛选：出链、入链、双向
- **链接类型** - 支持不同类型的关联（related, reference, etc.）
- **链接描述** - 可选的关联说明

#### 2. 图谱数据获取
- **完整图谱** - 获取用户的全部知识图谱
- **子图谱** - 以某个知识为中心，获取指定深度的子图
- **BFS遍历** - 广度优先搜索获取关联知识
- **深度控制** - 可配置遍历深度（1-5层）

#### 3. 自动关联检测
基于多个维度自动发现相关知识：
- **同分类** - 相同分类的知识（权重3分）
- **共同标签** - 有共同标签的知识（每个标签2分）
- **相似度评分** - 综合评分排序
- **推荐理由** - 显示关联原因

#### 4. 图谱统计
- 总知识条目数
- 总链接数
- 孤立条目数（无链接）
- 已连接条目数
- 平均每条目链接数

### API端点

#### 创建链接
```
POST /api/v1/knowledge/{knowledge_item_id}/links
```

**请求体：**
```json
{
  "target_id": "target-item-id",
  "link_type": "related",
  "description": "相关内容"
}
```

#### 获取链接
```
GET /api/v1/knowledge/{knowledge_item_id}/links?direction=both
```

**参数：**
- `direction`: outgoing（出链）, incoming（入链）, both（双向）

#### 删除链接
```
DELETE /api/v1/links/{link_id}
```

#### 获取图谱数据
```
GET /api/v1/graph?center_id=xxx&depth=2
```

**参数：**
- `center_id`: 中心节点ID（可选，不提供则返回完整图谱）
- `depth`: 遍历深度（1-5，默认2）

**响应：**
```json
{
  "nodes": [
    {
      "id": "xxx",
      "title": "知识标题",
      "is_published": true,
      "word_count": 1000,
      "category": "分类名",
      "tags": [{"name": "标签", "color": "#1890ff"}]
    }
  ],
  "edges": [
    {
      "id": "link-id",
      "source": "source-id",
      "target": "target-id",
      "type": "related",
      "description": "关联说明"
    }
  ],
  "center_id": "xxx",
  "depth": 2
}
```

#### 获取相关推荐
```
GET /api/v1/knowledge/{knowledge_item_id}/related?limit=10
```

**响应：**
```json
{
  "suggestions": [
    {
      "id": "xxx",
      "title": "相关知识",
      "score": 7,
      "reasons": ["同分类", "2个共同标签"],
      "category": "技术",
      "tags": [...]
    }
  ]
}
```

#### 图谱统计
```
GET /api/v1/graph/stats
```

---

## Task 9.2 - 数据备份和恢复 ✅

### 实现的文件
- `backend/app/services/backup.py` - 备份恢复服务

### 功能特性

#### 1. 完整备份
- **全量备份** - 备份所有用户数据
- **ZIP打包** - 压缩为ZIP文件
- **JSON格式** - 结构化数据存储
- **校验和** - SHA-256完整性验证
- **README** - 自动生成备份说明

**备份内容：**
- 知识条目（包含版本历史）
- 分类（层级结构）
- 标签
- 知识链接
- 元数据

#### 2. 增量备份
- **时间筛选** - 只备份指定时间后的变更
- **减少体积** - 只包含变更数据
- **快速备份** - 适合定期备份

#### 3. 备份验证
- **结构验证** - 检查必需字段
- **校验和验证** - 检测数据损坏
- **元数据检查** - 验证备份信息
- **统计信息** - 显示备份内容统计

#### 4. 数据恢复
- **选择性恢复** - 可选择恢复的数据类型
- **覆盖选项** - 可选是否覆盖现有数据
- **事务保护** - 失败自动回滚
- **恢复报告** - 详细的恢复结果

### 备份文件结构

```
backup.zip
├── backup.json          # 主备份数据
│   ├── metadata         # 备份元数据
│   │   ├── backup_version
│   │   ├── created_at
│   │   ├── user_id
│   │   └── checksum
│   ├── knowledge_items  # 知识条目数据
│   ├── categories       # 分类数据
│   ├── tags            # 标签数据
│   └── links           # 知识链接
└── README.txt          # 备份说明
```

### 使用示例

#### 创建完整备份
```python
from app.services.backup import BackupService

service = BackupService(db)
backup_file = await service.create_full_backup(user_id)

# 保存到文件
with open('backup.zip', 'wb') as f:
    f.write(backup_file.read())
```

#### 创建增量备份
```python
from datetime import datetime, timedelta

since = datetime.utcnow() - timedelta(days=7)
backup_file = await service.create_incremental_backup(user_id, since)
```

#### 验证备份
```python
with open('backup.zip', 'rb') as f:
    backup_file = BytesIO(f.read())
    
verification = await service.verify_backup(backup_file)
if verification['valid']:
    print(f"备份有效，包含 {verification['item_count']} 条知识")
else:
    print(f"备份无效：{verification['error']}")
```

#### 恢复备份
```python
options = {
    "restore_knowledge": True,
    "restore_categories": True,
    "restore_tags": True,
    "overwrite_existing": False
}

results = await service.restore_backup(backup_file, user_id, options)
print(f"恢复完成：{results}")
```

---

## 数据模型

### KnowledgeLink（知识链接）
```python
- id: 链接ID
- source_id: 源知识ID
- target_id: 目标知识ID
- link_type: 链接类型（related, reference, etc.）
- description: 链接描述
- created_at: 创建时间
```

### 备份元数据
```json
{
  "backup_version": "1.0",
  "created_at": "2024-01-01T00:00:00",
  "user_id": "user-id",
  "checksum": "sha256-hash",
  "backup_type": "full|incremental"
}
```

---

## 技术实现

### 知识图谱

#### BFS遍历算法
```python
queue = [(center_id, 0)]
visited = set([center_id])

while queue:
    item_id, depth = queue.pop(0)
    if depth > max_depth:
        continue
    
    # 获取链接
    links = get_links(item_id)
    for link in links:
        other_id = get_other_end(link, item_id)
        if other_id not in visited:
            visited.add(other_id)
            queue.append((other_id, depth + 1))
```

#### 相似度计算
```python
score = 0
if same_category:
    score += 3
score += common_tags_count * 2
```

### 数据备份

#### 校验和计算
```python
data_str = json.dumps(backup_data, sort_keys=True)
checksum = hashlib.sha256(data_str.encode()).hexdigest()
```

#### ZIP压缩
```python
with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('backup.json', json_data)
    zf.writestr('README.txt', readme)
```

---

## 安全特性

1. **权限验证**
   - 只能操作自己的数据
   - JWT认证保护

2. **数据完整性**
   - SHA-256校验和
   - 结构验证
   - 事务保护

3. **防止循环引用**
   - 不能链接到自己
   - 检测重复链接

---

## 性能优化

1. **关系预加载**
   - selectinload避免N+1查询
   - 批量加载关联数据

2. **深度限制**
   - 图谱遍历深度限制（1-5）
   - 防止过度查询

3. **增量备份**
   - 只备份变更数据
   - 减少备份时间和体积

---

## 未来改进

### 知识图谱
1. **可视化增强**
   - 力导向图布局
   - 节点聚类
   - 交互式探索

2. **智能推荐**
   - 基于内容的相似度
   - 协同过滤
   - 机器学习模型

3. **图谱分析**
   - 中心性分析
   - 社区发现
   - 路径查找

### 数据备份
1. **自动备份**
   - 定时备份任务
   - 备份策略配置
   - 备份保留策略

2. **云存储**
   - S3/OSS集成
   - 自动上传
   - 异地备份

3. **增量恢复**
   - 支持增量恢复
   - 冲突解决
   - 版本合并

---

## 下一步

- 前端知识图谱可视化（D3.js）
- 备份管理界面
- 自动备份调度

---

**当前状态**: 知识图谱和备份功能后端已完成，API可用。
