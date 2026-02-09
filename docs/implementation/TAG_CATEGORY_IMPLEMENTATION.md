# 标签和分类系统实现文档

## 概述

本文档描述了知识管理平台的标签和分类系统实现。

## 实现的功能

### Task 5.1 - 标签管理系统 ✅

**文件：**
- `backend/app/services/tag.py` - 标签业务逻辑服务
- `backend/app/schemas/tag.py` - 标签Pydantic schemas
- `backend/app/api/v1/endpoints/tags.py` - 标签REST API端点
- `backend/app/models/tag.py` - 标签数据模型（已存在）

**功能特性：**
1. **CRUD操作**
   - 创建标签（带颜色和描述）
   - 获取单个标签
   - 列表查询（支持搜索和系统标签过滤）
   - 更新标签
   - 删除标签（软删除）

2. **高级功能**
   - 标签合并：将一个标签合并到另一个标签
   - 热门标签：按使用次数排序
   - 自动补全：根据前缀搜索标签
   - 使用统计：跟踪标签使用次数

3. **API端点**
   - `POST /api/v1/tags` - 创建标签
   - `GET /api/v1/tags` - 列表查询（支持search参数）
   - `GET /api/v1/tags/{tag_id}` - 获取单个标签
   - `PUT /api/v1/tags/{tag_id}` - 更新标签
   - `DELETE /api/v1/tags/{tag_id}` - 删除标签
   - `GET /api/v1/tags/popular` - 获取热门标签
   - `GET /api/v1/tags/autocomplete?prefix=xxx` - 自动补全
   - `POST /api/v1/tags/merge` - 合并标签

### Task 5.2 - 分类系统 ✅

**文件：**
- `backend/app/services/category.py` - 分类业务逻辑服务
- `backend/app/schemas/category.py` - 分类Pydantic schemas
- `backend/app/api/v1/endpoints/categories.py` - 分类REST API端点
- `backend/app/models/category.py` - 分类数据模型（已存在）

**功能特性：**
1. **CRUD操作**
   - 创建分类（支持父子层级）
   - 获取单个分类
   - 列表查询（支持按父分类过滤）
   - 更新分类
   - 删除分类（软删除，可选级联删除子分类）

2. **层级结构**
   - 无限层级嵌套
   - 父子关系管理
   - 完整路径显示（如：技术 > 编程 > Python）
   - 深度计算
   - 祖先和后代查询

3. **高级功能**
   - 分类树：获取完整的树形结构
   - 移动分类：更改父分类
   - 合并分类：将一个分类合并到另一个
   - 统计信息：知识条目数量、子分类数量等
   - 循环引用检测：防止分类成为自己的子孙

4. **API端点**
   - `POST /api/v1/categories` - 创建分类
   - `GET /api/v1/categories` - 列表查询（支持parent_id过滤）
   - `GET /api/v1/categories/tree` - 获取完整树形结构
   - `GET /api/v1/categories/{category_id}` - 获取单个分类
   - `GET /api/v1/categories/{category_id}/stats` - 获取分类统计
   - `PUT /api/v1/categories/{category_id}` - 更新分类
   - `DELETE /api/v1/categories/{category_id}` - 删除分类
   - `POST /api/v1/categories/{category_id}/move` - 移动分类
   - `POST /api/v1/categories/merge` - 合并分类

## 数据模型

### Tag模型
```python
- id: 唯一标识
- name: 标签名称（最多50字符）
- description: 描述
- user_id: 所属用户
- color: 颜色（十六进制）
- usage_count: 使用次数
- is_active: 是否激活
- is_system: 是否系统标签
- created_at/updated_at: 时间戳
```

### Category模型
```python
- id: 唯一标识
- name: 分类名称（最多100字符）
- description: 描述
- parent_id: 父分类ID
- user_id: 所属用户
- color: 颜色（十六进制）
- icon: 图标
- sort_order: 排序顺序
- is_active: 是否激活
- created_at/updated_at: 时间戳
```

## 安全特性

1. **权限控制**
   - 所有操作需要JWT认证
   - 用户只能操作自己的标签和分类
   - 系统标签不可修改或删除

2. **数据验证**
   - 名称唯一性检查（同一用户、同一层级）
   - 颜色格式验证（十六进制）
   - 循环引用检测（分类）
   - 输入长度限制

3. **软删除**
   - 标签和分类使用软删除
   - 保留数据完整性
   - 可恢复删除的数据

## 使用示例

### 创建标签
```bash
curl -X POST http://localhost:8000/api/v1/tags \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "description": "Python编程相关",
    "color": "#3776ab"
  }'
```

### 创建分类
```bash
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "编程",
    "description": "编程技术相关",
    "parent_id": null,
    "color": "#e74c3c",
    "icon": "code"
  }'
```

### 获取分类树
```bash
curl -X GET http://localhost:8000/api/v1/categories/tree \
  -H "Authorization: Bearer <token>"
```

## 下一步

- Task 6.1: 集成Elasticsearch搜索服务
- Task 6.2: 实现高级搜索功能

## 注意事项

1. 标签和分类都支持颜色自定义，用于前端展示
2. 分类支持无限层级，但建议不超过5层以保持简洁
3. 标签的usage_count会在知识条目关联时自动更新
4. 删除分类时需要考虑子分类和关联的知识条目
