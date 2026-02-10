# 前端错误处理修复 / Frontend Error Handling Fix

**修复时间**: 2026-02-10  
**状态**: ✅ 已完成

## 问题描述

用户在界面创建知识时遇到React运行时错误：

```
Uncaught runtime errors:
×ERROR
Objects are not valid as a React child (found: object with keys {type, loc, msg, input}). 
If you meant to render a collection of children, use an array instead.
```

## 根本原因

当后端返回FastAPI验证错误时，错误格式是一个对象数组：

```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "title"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

前端代码直接将这个对象传递给 `message.error()`，导致React尝试渲染对象而报错：

```typescript
// ❌ 错误的处理方式
message.error(error.response?.data?.detail || '保存失败');
// 当 detail 是对象数组时，React无法渲染
```

## 解决方案

### 1. 创建错误处理工具函数

创建 `frontend/src/utils/errorHandler.ts`：

```typescript
export const formatErrorMessage = (
  error: any, 
  defaultMessage: string = '操作失败'
): string => {
  if (!error?.response?.data?.detail) {
    return defaultMessage;
  }

  const detail = error.response.data.detail;

  // Handle FastAPI validation errors (array format)
  if (Array.isArray(detail)) {
    return detail
      .map((err: any) => {
        const location = err.loc?.slice(1).join('.') || 'unknown';
        return `${location}: ${err.msg}`;
      })
      .join('; ');
  }

  // Handle string error messages
  if (typeof detail === 'string') {
    return detail;
  }

  return defaultMessage;
};
```

### 2. 更新组件使用工具函数

**KnowledgeEditorPage.tsx**:
```typescript
import { formatErrorMessage } from '@/utils/errorHandler';

// ✅ 正确的处理方式
catch (error: any) {
  message.error(formatErrorMessage(error, '保存失败'));
}
```

**RelatedKnowledgeSection.tsx**:
```typescript
import { formatErrorMessage } from '@/utils/errorHandler';

catch (error: any) {
  message.error(formatErrorMessage(error, '创建关联失败'));
}
```

## 错误格式处理

### FastAPI验证错误
```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "title"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

**格式化后**:
```
title: Input should be a valid string
```

### 字符串错误
```json
{
  "detail": "Knowledge item not found"
}
```

**格式化后**:
```
Knowledge item not found
```

### 多个验证错误
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required"
    },
    {
      "loc": ["body", "content"],
      "msg": "Field required"
    }
  ]
}
```

**格式化后**:
```
title: Field required; content: Field required
```

## 修复的文件

1. **frontend/src/utils/errorHandler.ts** (新建)
   - `formatErrorMessage()` - 格式化错误消息
   - `extractValidationErrors()` - 提取表单验证错误

2. **frontend/src/pages/knowledge/KnowledgeEditorPage.tsx**
   - 导入 `formatErrorMessage`
   - 更新 `handleSave` 错误处理

3. **frontend/src/components/knowledge/RelatedKnowledgeSection.tsx**
   - 导入 `formatErrorMessage`
   - 更新 `createLink` 错误处理

## 使用示例

### 基本用法
```typescript
import { formatErrorMessage } from '@/utils/errorHandler';

try {
  await api.post('/knowledge', data);
} catch (error) {
  message.error(formatErrorMessage(error, '创建失败'));
}
```

### 自定义默认消息
```typescript
message.error(formatErrorMessage(error, '自定义错误消息'));
```

### 提取表单验证错误
```typescript
import { extractValidationErrors } from '@/utils/errorHandler';

try {
  await api.post('/knowledge', data);
} catch (error) {
  const fieldErrors = extractValidationErrors(error);
  // fieldErrors = { title: 'Field required', content: 'Field required' }
  
  // 可以用于设置表单字段错误
  form.setFields(
    Object.entries(fieldErrors).map(([name, error]) => ({
      name,
      errors: [error],
    }))
  );
}
```

## 最佳实践

### 1. 统一错误处理
所有API调用都应该使用 `formatErrorMessage` 处理错误：

```typescript
// ✅ 推荐
catch (error: any) {
  message.error(formatErrorMessage(error, '操作失败'));
}

// ❌ 不推荐
catch (error: any) {
  message.error(error.response?.data?.detail || '操作失败');
}
```

### 2. 提供有意义的默认消息
```typescript
// ✅ 好的默认消息
formatErrorMessage(error, '创建知识失败')
formatErrorMessage(error, '更新分类失败')
formatErrorMessage(error, '删除标签失败')

// ❌ 不够具体的默认消息
formatErrorMessage(error, '失败')
formatErrorMessage(error, '错误')
```

### 3. 记录错误日志
```typescript
catch (error: any) {
  console.error('Failed to save:', error);
  message.error(formatErrorMessage(error, '保存失败'));
}
```

## 其他需要修复的地方

建议在以下文件中也应用相同的错误处理：

- [ ] `frontend/src/pages/categories/CategoriesPage.tsx`
- [ ] `frontend/src/pages/tags/TagsPage.tsx`
- [ ] `frontend/src/pages/users/UsersManagementPage.tsx`
- [ ] `frontend/src/pages/sync/SyncManagementPage.tsx`
- [ ] `frontend/src/pages/import/ImportManagementPage.tsx`
- [ ] 其他所有使用 `message.error(error.response?.data?.detail)` 的地方

## 验证

### 测试场景1: 必填字段验证
1. 打开创建知识页面
2. 不填写标题，直接点击保存
3. ✅ 应该显示: "title: Field required"

### 测试场景2: 类型验证
1. 通过API发送错误类型的数据
2. ✅ 应该显示格式化的错误消息，而不是React错误

### 测试场景3: 字符串错误
1. 尝试访问不存在的资源
2. ✅ 应该显示: "Knowledge item not found"

## 相关文档

- [前端API路径修复](FRONTEND_API_PATH_FIX.md)
- [知识图谱修复总结](KNOWLEDGE_GRAPH_FIX_SUMMARY.md)

## 总结

✅ **错误处理问题已修复**

修复内容：
- ✅ 创建错误处理工具函数
- ✅ 修复知识编辑页面错误处理
- ✅ 修复关联知识组件错误处理
- ✅ 支持FastAPI验证错误格式
- ✅ 支持字符串错误消息
- ✅ 提供清晰的错误提示

用户现在可以看到清晰、可读的错误消息，而不会遇到React运行时错误！

---

**修复人**: Kiro AI Assistant  
**版本**: v1.2.0  
**状态**: ✅ 已完成并验证
