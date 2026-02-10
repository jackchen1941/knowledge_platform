# 前端API路径统一修复 / Frontend API Path Unified Fix

**修复时间**: 2026-02-10  
**状态**: ✅ 已完成

## 问题概述

前端多个页面在调用API时使用了完整路径 `/api/v1/...`，但 `api.ts` 的 `baseURL` 已经配置为 `/api/v1`，导致实际请求路径变成 `/api/v1/api/v1/...`，造成404错误或功能异常。

## 根本原因

**axios配置**:
```typescript
// frontend/src/services/api.ts
const instance = axios.create({
  baseURL: '/api/v1',  // 已经包含 /api/v1
});
```

**错误的调用方式**:
```typescript
// ❌ 错误：重复了 /api/v1
await api.get('/api/v1/graph')
// 实际请求: /api/v1 + /api/v1/graph = /api/v1/api/v1/graph
```

**正确的调用方式**:
```typescript
// ✅ 正确：使用相对路径
await api.get('/graph')
// 实际请求: /api/v1 + /graph = /api/v1/graph
```

## 修复的文件

### 1. RelatedKnowledgeSection.tsx
**文件**: `frontend/src/components/knowledge/RelatedKnowledgeSection.tsx`

**修复内容**:
- 获取链接: `/api/v1/knowledge/${id}/links` → `/knowledge/${id}/links`
- 获取推荐: `/api/v1/knowledge/${id}/related` → `/knowledge/${id}/related`
- 搜索知识: `/api/v1/search` → `/search`
- 创建链接: `/api/v1/knowledge/${id}/links` → `/knowledge/${id}/links`
- 删除链接: `/api/v1/links/${id}` → `/links/${id}`
- 响应字段: `res.data.results` → `res.data.items`

**影响功能**: 知识关联、搜索、推荐

### 2. KnowledgeGraphPage.tsx
**文件**: `frontend/src/pages/knowledge/KnowledgeGraphPage.tsx`

**修复内容**:
- 获取图谱数据: `/api/v1/graph` → `/graph`
- 获取统计: `/api/v1/graph/stats` → `/graph/stats`

**影响功能**: 知识图谱可视化

### 3. SyncManagementPage.tsx
**文件**: `frontend/src/pages/sync/SyncManagementPage.tsx`

**修复内容**:
- 获取设备列表: `/api/v1/sync/devices` → `/sync/devices`
- 获取冲突: `/api/v1/sync/conflicts` → `/sync/conflicts`
- 获取统计: `/api/v1/sync/stats` → `/sync/stats`
- 注册设备: `/api/v1/sync/devices/register` → `/sync/devices/register`
- 同步数据: `/api/v1/sync/pull` → `/sync/pull`

**影响功能**: 多设备同步管理

## 修复对比

### 修复前
```typescript
// RelatedKnowledgeSection.tsx
await api.get(`/api/v1/knowledge/${knowledgeId}/links`)
await api.get(`/api/v1/search?q=${keyword}`)
await api.post(`/api/v1/knowledge/${knowledgeId}/links`, data)

// KnowledgeGraphPage.tsx
await api.get('/api/v1/graph', { params })
await api.get('/api/v1/graph/stats')

// SyncManagementPage.tsx
await api.get('/api/v1/sync/devices')
await api.post('/api/v1/sync/pull', data)
```

### 修复后
```typescript
// RelatedKnowledgeSection.tsx
await api.get(`/knowledge/${knowledgeId}/links`)
await api.get(`/search?q=${keyword}`)
await api.post(`/knowledge/${knowledgeId}/links`, data)

// KnowledgeGraphPage.tsx
await api.get('/graph', { params })
await api.get('/graph/stats')

// SyncManagementPage.tsx
await api.get('/sync/devices')
await api.post('/sync/pull', data)
```

## 统计

**修复文件数**: 3个
**修复API调用**: 11处
**修复响应字段**: 1处

| 文件 | API调用修复 | 其他修复 |
|------|------------|---------|
| RelatedKnowledgeSection.tsx | 5处 | 1处响应字段 |
| KnowledgeGraphPage.tsx | 2处 | - |
| SyncManagementPage.tsx | 5处 | - |

## 验证

### 知识图谱功能
```bash
# 测试图谱API
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/graph"
# ✅ 返回图谱数据

curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/graph/stats"
# ✅ 返回统计数据
```

### 前端测试
1. **知识关联**
   - 打开知识详情页
   - 点击"添加关联"
   - 搜索知识 ✅
   - 创建关联 ✅
   - 查看关联列表 ✅

2. **知识图谱**
   - 访问知识图谱页面
   - 图谱数据加载 ✅
   - 统计信息显示 ✅
   - 节点交互正常 ✅

3. **同步管理**
   - 访问同步管理页面
   - 设备列表加载 ✅
   - 注册设备功能 ✅
   - 同步功能正常 ✅

## 最佳实践

### 1. API调用规范

**DO ✅**:
```typescript
// 使用相对路径
api.get('/users')
api.post('/knowledge', data)
api.put('/knowledge/123', data)
api.delete('/knowledge/123')
```

**DON'T ❌**:
```typescript
// 不要包含baseURL
api.get('/api/v1/users')
api.post('/api/v1/knowledge', data)
```

### 2. 响应数据处理

**DO ✅**:
```typescript
// 检查实际响应格式
const res = await api.get('/search')
console.log(res.data)  // 查看实际结构
const items = res.data.items || []  // 使用正确字段
```

**DON'T ❌**:
```typescript
// 不要假设字段名
const results = res.data.results  // 可能不存在
```

### 3. TypeScript类型定义

**推荐**:
```typescript
interface SearchResponse {
  items: KnowledgeItem[];
  total: number;
  page: number;
  page_size: number;
}

const res = await api.get<SearchResponse>('/search')
const items = res.data.items  // 类型安全
```

### 4. 检查清单

开发新功能时：
- [ ] 确认 axios 实例的 baseURL 配置
- [ ] 使用相对路径调用API
- [ ] 检查后端API的响应格式
- [ ] 使用正确的字段名访问数据
- [ ] 添加TypeScript类型定义
- [ ] 测试API调用是否正常

## 调试技巧

### 1. 检查实际请求URL
```javascript
// 在浏览器开发者工具 Network 面板查看
// 实际请求的完整URL
```

### 2. 查看响应数据结构
```typescript
const res = await api.get('/search')
console.log('Response:', res.data)  // 查看实际结构
```

### 3. 检查后端日志
```bash
# 查看后端请求日志
tail -f backend/logs/app.log
```

### 4. 使用curl测试
```bash
# 直接测试后端API
curl "http://localhost:8000/api/v1/graph"
```

## 相关文档

- [知识图谱修复总结](KNOWLEDGE_GRAPH_FIX_SUMMARY.md)
- [知识图谱测试结果](KNOWLEDGE_GRAPH_TEST_RESULTS.md)
- [API服务配置](frontend/src/services/api.ts)

## 总结

✅ **所有前端API路径问题已修复**

修复范围：
- ✅ 知识关联功能
- ✅ 知识图谱可视化
- ✅ 多设备同步管理

所有功能现在都可以正常使用，不再出现路径重复导致的404错误！

---

**修复人**: Kiro AI Assistant  
**版本**: v1.2.0  
**状态**: ✅ 已完成并验证
