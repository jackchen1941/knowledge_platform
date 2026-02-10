# 知识管理平台 - 产品需求文档 (PRD)
# Knowledge Management Platform - Product Requirements Document

**文档版本**: v1.0  
**创建日期**: 2026-02-10  
**产品版本**: v1.2.0  
**文档状态**: 正式版

---

## 📋 文档说明

### 为什么需要这份文档？

这份PRD是基于实际开发过程中逐步明确的需求整理而成。如果在项目启动时就有这样一份完整的需求文档，开发效率会显著提升：

- **减少返工**: 明确的需求避免功能反复修改
- **提高效率**: 开发人员可以一次性实现完整功能
- **降低沟通成本**: 减少需求澄清的往返次数
- **保证质量**: 完整的验收标准确保功能符合预期

### 文档结构

本PRD遵循专业产品需求文档的标准结构：

1. **产品概述** - 产品定位、目标用户、核心价值
2. **功能需求** - 详细的功能描述、用户故事、验收标准
3. **非功能需求** - 性能、安全、可用性等要求
4. **技术架构** - 技术选型、系统架构、数据模型
5. **接口规范** - API设计、数据格式、错误处理
6. **用户体验** - 交互设计、界面规范、响应式设计
7. **测试要求** - 测试策略、测试用例、验收标准
8. **部署运维** - 部署方案、监控告警、备份恢复

---

## 1. 产品概述

### 1.1 产品定位

一个现代化的个人/团队知识管理平台，类似Notion + Obsidian的结合体，支持：
- 结构化知识管理（文件夹、分类、标签）
- 知识图谱可视化（双向链接、关系网络）
- 多源导入（URL、Markdown、Notion、CSDN等）
- 实时协作（WebSocket、通知系统）
- 数据安全（备份、导出、权限控制）

### 1.2 目标用户

**主要用户**:
- 个人知识工作者（程序员、研究人员、作家）
- 小型团队（5-20人）
- 学习者和教育工作者

**用户画像**:
- 需要管理大量碎片化知识
- 重视知识之间的关联关系
- 需要从多个来源导入内容
- 希望数据可控、可导出
- 对隐私和安全有要求

### 1.3 核心价值

1. **知识网络化**: 通过知识图谱建立知识之间的关联
2. **多源整合**: 支持从多个平台导入内容
3. **高效检索**: 全文搜索 + 标签分类 + 图谱导航
4. **数据安全**: 本地部署 + 完整备份 + 数据导出
5. **易于使用**: 现代化UI + 快捷操作 + 智能推荐



---

## 2. 功能需求

### 2.1 用户认证与权限管理

#### 2.1.1 用户注册与登录

**功能描述**:
- 支持邮箱+密码注册/登录
- JWT Token认证机制
- 记住登录状态（7天）
- 密码强度验证（最少8位，包含字母和数字）

**用户故事**:
```
作为新用户，我希望能够快速注册账号，以便开始使用系统
作为老用户，我希望能够安全登录，并保持登录状态
```

**验收标准**:
- [ ] 注册时验证邮箱格式和密码强度
- [ ] 登录成功后返回JWT Token
- [ ] Token有效期为7天
- [ ] 密码使用bcrypt加密存储
- [ ] 登录失败3次后显示验证码（可选）

**API接口**:
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

#### 2.1.2 用户管理（管理员功能）

**功能描述**:
- 查看用户列表（分页、搜索、筛选）
- 创建/编辑/删除用户
- 用户状态管理（激活/禁用）
- 用户统计信息

**用户故事**:
```
作为管理员，我希望能够管理所有用户账号
作为管理员，我希望能够查看用户统计数据
```

**验收标准**:
- [ ] 只有超级管理员可以访问用户管理功能
- [ ] 支持按用户名、邮箱搜索
- [ ] 支持按状态筛选（活跃/禁用）
- [ ] 显示用户统计（总数、活跃数、超级管理员数）
- [ ] 删除用户前需要二次确认

**API接口**:
```
GET    /api/v1/users          # 获取用户列表
POST   /api/v1/users          # 创建用户
GET    /api/v1/users/{id}     # 获取用户详情
PUT    /api/v1/users/{id}     # 更新用户
DELETE /api/v1/users/{id}     # 删除用户
GET    /api/v1/users/stats    # 用户统计
```

#### 2.1.3 角色与权限

**功能描述**:
- 基于角色的访问控制（RBAC）
- 预定义角色：超级管理员、管理员、普通用户
- 细粒度权限控制（读、写、删除、管理）

**权限矩阵**:
| 功能 | 超级管理员 | 管理员 | 普通用户 |
|------|-----------|--------|---------|
| 用户管理 | ✅ | ❌ | ❌ |
| 知识管理 | ✅ | ✅ | ✅（仅自己） |
| 系统设置 | ✅ | ✅ | ❌ |
| 数据导出 | ✅ | ✅ | ✅（仅自己） |



### 2.2 知识管理核心功能

#### 2.2.1 知识创建与编辑

**功能描述**:
- Markdown编辑器（支持实时预览）
- 富文本编辑（标题、列表、代码块、表格）
- 自动保存（每30秒或内容变化时）
- 版本历史（保留最近10个版本）
- 附件上传（图片、文档、最大10MB）

**用户故事**:
```
作为用户，我希望能够使用Markdown编写知识
作为用户，我希望编辑时能够实时预览效果
作为用户，我希望系统能够自动保存，避免内容丢失
```

**验收标准**:
- [ ] 支持标准Markdown语法
- [ ] 实时预览延迟 < 100ms
- [ ] 自动保存成功后显示提示
- [ ] 版本历史可以查看和恢复
- [ ] 附件上传支持拖拽

**字段定义**:
```typescript
interface Knowledge {
  id: string;              // UUID
  title: string;           // 标题（必填，最长200字符）
  content: string;         // 内容（Markdown格式）
  summary?: string;        // 摘要（可选，最长500字符）
  category_id?: string;    // 分类ID
  tags: string[];          // 标签列表
  is_public: boolean;      // 是否公开
  is_pinned: boolean;      // 是否置顶
  created_at: datetime;    // 创建时间
  updated_at: datetime;    // 更新时间
  created_by: string;      // 创建者ID
}
```

#### 2.2.2 知识分类与标签

**功能描述**:
- 树形分类结构（最多3层）
- 标签系统（支持颜色标记）
- 批量分类/打标签
- 分类统计（知识数量）

**用户故事**:
```
作为用户，我希望能够用分类组织知识结构
作为用户，我希望能够用标签标记知识特征
作为用户，我希望能够快速筛选特定分类或标签的知识
```

**验收标准**:
- [ ] 分类支持拖拽排序
- [ ] 标签支持自定义颜色（8种预设颜色）
- [ ] 删除分类时提示关联的知识数量
- [ ] 支持批量添加/移除标签

**API接口**:
```
GET    /api/v1/categories           # 获取分类树
POST   /api/v1/categories           # 创建分类
PUT    /api/v1/categories/{id}      # 更新分类
DELETE /api/v1/categories/{id}      # 删除分类

GET    /api/v1/tags                 # 获取标签列表
POST   /api/v1/tags                 # 创建标签
PUT    /api/v1/tags/{id}            # 更新标签
DELETE /api/v1/tags/{id}            # 删除标签
```

#### 2.2.3 知识搜索

**功能描述**:
- 全文搜索（标题 + 内容）
- 高级筛选（分类、标签、日期范围）
- 搜索结果高亮
- 搜索历史（最近10条）
- 搜索建议（自动补全）

**用户故事**:
```
作为用户，我希望能够快速找到需要的知识
作为用户，我希望搜索结果能够高亮显示关键词
作为用户，我希望能够组合多个条件进行精确搜索
```

**验收标准**:
- [ ] 搜索响应时间 < 300ms
- [ ] 支持中文分词
- [ ] 搜索结果按相关度排序
- [ ] 高亮显示匹配的关键词
- [ ] 支持搜索语法（AND、OR、NOT）

**搜索参数**:
```typescript
interface SearchParams {
  q: string;                    // 搜索关键词
  category_id?: string;         // 分类筛选
  tags?: string[];              // 标签筛选
  date_from?: string;           // 开始日期
  date_to?: string;             // 结束日期
  sort_by?: 'relevance' | 'date' | 'title';
  page?: number;
  page_size?: number;
}
```



### 2.3 知识图谱功能（核心特色）

#### 2.3.1 双向链接

**功能描述**:
- 知识之间建立有向链接
- 7种链接类型：
  - `related` - 相关知识
  - `prerequisite` - 前置知识
  - `derived` - 衍生知识
  - `similar` - 相似知识
  - `reference` - 引用
  - `example` - 示例
  - `comparison` - 对比
- 显示出链（Outgoing）和入链（Incoming）
- 链接描述（可选，说明关联原因）

**用户故事**:
```
作为用户，我希望能够建立知识之间的关联关系
作为用户，我希望能够看到某个知识的所有相关知识
作为用户，我希望能够通过链接快速跳转到相关知识
```

**验收标准**:
- [ ] 创建链接时可以选择链接类型
- [ ] 显示链接时区分出链和入链
- [ ] 点击链接可以跳转到目标知识
- [ ] 删除知识时自动删除相关链接
- [ ] 防止创建重复链接

**数据模型**:
```typescript
interface KnowledgeLink {
  id: string;
  from_item_id: string;      // 源知识ID
  to_item_id: string;        // 目标知识ID
  link_type: LinkType;       // 链接类型
  description?: string;      // 链接描述
  created_at: datetime;
  created_by: string;
}

type LinkType = 'related' | 'prerequisite' | 'derived' | 
                'similar' | 'reference' | 'example' | 'comparison';
```

#### 2.3.2 智能推荐

**功能描述**:
- 基于分类推荐（同分类的知识）
- 基于标签推荐（共同标签越多，相似度越高）
- 推荐算法：
  - 同分类：相似度 +3
  - 每个共同标签：相似度 +2
  - 按相似度降序排列
- 显示推荐原因

**用户故事**:
```
作为用户，我希望系统能够推荐相关的知识
作为用户，我希望了解推荐的原因
作为用户，我希望能够快速添加推荐的关联
```

**验收标准**:
- [ ] 推荐结果按相似度排序
- [ ] 显示推荐原因（同分类/共同标签）
- [ ] 排除已经建立链接的知识
- [ ] 排除当前知识本身
- [ ] 最多显示10条推荐

#### 2.3.3 知识图谱可视化

**功能描述**:
- 使用D3.js或类似库实现图谱可视化
- 节点表示知识，边表示链接
- 支持缩放、拖拽、筛选
- 节点大小表示链接数量
- 不同链接类型用不同颜色表示

**用户故事**:
```
作为用户，我希望能够可视化查看知识网络
作为用户，我希望能够通过图谱发现知识之间的关系
作为用户，我希望能够在图谱中快速导航
```

**验收标准**:
- [ ] 图谱加载时间 < 500ms（100个节点）
- [ ] 支持鼠标滚轮缩放
- [ ] 支持拖拽节点
- [ ] 点击节点跳转到知识详情
- [ ] 支持按分类/标签筛选显示

**图谱统计**:
```typescript
interface GraphStats {
  total_nodes: number;        // 总节点数
  total_links: number;        // 总链接数
  isolated_nodes: number;     // 孤立节点数
  avg_links: number;          // 平均链接数
  max_links: number;          // 最大链接数
  link_types: {               // 各类型链接统计
    [key: string]: number;
  };
}
```



### 2.4 导入导出功能

#### 2.4.1 URL导入

**功能描述**:
- 支持导入网页内容
- 自动提取标题、正文、图片
- 保留原始链接
- 支持常见网站（Medium、知乎、CSDN等）

**用户故事**:
```
作为用户，我希望能够快速保存网页内容
作为用户，我希望导入的内容格式整洁
作为用户，我希望能够追溯原始来源
```

**验收标准**:
- [ ] 支持HTTP/HTTPS协议
- [ ] 自动提取网页标题作为知识标题
- [ ] 转换HTML为Markdown格式
- [ ] 保存原始URL到元数据
- [ ] 导入失败时显示明确的错误信息

**技术要求**:
- 使用BeautifulSoup解析HTML
- 使用html2text转换为Markdown
- 处理字符编码问题
- 超时时间：30秒
- 最大内容大小：5MB

#### 2.4.2 Markdown文件导入

**功能描述**:
- 支持单个或批量导入.md文件
- 自动解析Front Matter（YAML格式）
- 提取标题、标签、分类等元数据
- 支持拖拽上传

**Front Matter示例**:
```yaml
---
title: Python基础教程
category: 编程
tags: [Python, 教程, 基础]
date: 2026-02-10
---
```

**验收标准**:
- [ ] 支持标准Markdown语法
- [ ] 正确解析Front Matter
- [ ] 批量导入显示进度
- [ ] 导入失败的文件显示错误原因
- [ ] 支持预览导入结果

#### 2.4.3 Notion导入（适配器模式）

**功能描述**:
- 通过Notion API导入页面
- 支持导入页面结构（父子关系）
- 转换Notion Block为Markdown
- 保留页面属性（标签、日期等）

**配置要求**:
```typescript
interface NotionConfig {
  api_key: string;           // Notion API密钥
  database_id?: string;      // 数据库ID（可选）
  page_id?: string;          // 页面ID（可选）
}
```

**验收标准**:
- [ ] 正确转换Notion Block类型
- [ ] 保留页面层级关系
- [ ] 导入图片和附件
- [ ] 显示导入进度
- [ ] 支持增量同步

#### 2.4.4 数据导出

**功能描述**:
- 支持导出格式：JSON、Markdown、HTML
- 支持全量导出或选择性导出
- 导出包含元数据和附件
- 生成压缩包下载

**导出选项**:
```typescript
interface ExportOptions {
  format: 'json' | 'markdown' | 'html';
  include_attachments: boolean;
  include_metadata: boolean;
  knowledge_ids?: string[];    // 指定导出的知识ID
  category_id?: string;        // 按分类导出
  date_from?: string;          // 日期范围
  date_to?: string;
}
```

**验收标准**:
- [ ] JSON格式包含完整数据结构
- [ ] Markdown格式保留格式和链接
- [ ] HTML格式可以离线浏览
- [ ] 附件打包在attachments目录
- [ ] 生成导出清单文件



### 2.5 协作与通知

#### 2.5.1 实时通知系统

**功能描述**:
- WebSocket实时推送通知
- 通知类型：
  - 系统通知（更新、维护）
  - 知识通知（评论、@提及）
  - 协作通知（共享、权限变更）
- 通知中心（查看历史通知）
- 通知设置（开启/关闭特定类型）

**用户故事**:
```
作为用户，我希望能够实时收到重要通知
作为用户，我希望能够查看历史通知
作为用户，我希望能够控制接收哪些类型的通知
```

**验收标准**:
- [ ] 通知实时推送延迟 < 1秒
- [ ] 未读通知显示红点提示
- [ ] 点击通知跳转到相关页面
- [ ] 支持标记已读/全部已读
- [ ] 通知保留30天

**数据模型**:
```typescript
interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  content: string;
  link?: string;              // 跳转链接
  is_read: boolean;
  created_at: datetime;
}

type NotificationType = 'system' | 'knowledge' | 'collaboration';
```

#### 2.5.2 多设备同步

**功能描述**:
- 支持多设备登录
- 数据实时同步
- 冲突检测与解决
- 离线编辑支持

**同步策略**:
- 使用版本号进行冲突检测
- 最后写入优先（Last Write Wins）
- 冲突时提示用户选择版本
- 离线编辑在联网后自动同步

**验收标准**:
- [ ] 多设备数据一致性
- [ ] 同步延迟 < 2秒
- [ ] 冲突时不丢失数据
- [ ] 显示同步状态（同步中/已同步/冲突）
- [ ] 支持手动触发同步

### 2.6 数据分析与统计

#### 2.6.1 仪表盘

**功能描述**:
- 知识统计（总数、今日新增、本周新增）
- 分类分布（饼图）
- 标签云（词云图）
- 活跃度趋势（折线图，最近30天）
- 知识图谱统计（节点数、链接数）

**用户故事**:
```
作为用户，我希望能够了解我的知识库概况
作为用户，我希望能够看到知识增长趋势
作为用户，我希望能够发现常用的标签和分类
```

**验收标准**:
- [ ] 仪表盘加载时间 < 1秒
- [ ] 图表支持交互（点击、悬停）
- [ ] 数据每小时更新一次
- [ ] 支持自定义时间范围
- [ ] 支持导出统计报告

#### 2.6.2 知识分析

**功能描述**:
- 知识质量评分（完整度、链接数、更新频率）
- 热门知识排行（浏览次数、链接数）
- 孤立知识检测（无链接的知识）
- 知识推荐（基于阅读历史）

**质量评分算法**:
```
质量分 = 内容完整度(40%) + 链接丰富度(30%) + 更新活跃度(30%)

内容完整度 = (标题 + 内容 + 摘要 + 分类 + 标签) / 5
链接丰富度 = min(链接数 / 5, 1)
更新活跃度 = 1 - (距上次更新天数 / 365)
```

**验收标准**:
- [ ] 质量评分准确反映知识完整度
- [ ] 热门知识每日更新
- [ ] 孤立知识提供关联建议
- [ ] 推荐算法准确率 > 70%



---

## 3. 非功能需求

### 3.1 性能要求

| 指标 | 要求 | 测量方法 |
|------|------|---------|
| 页面加载时间 | < 2秒 | Chrome DevTools |
| API响应时间 | < 200ms (P95) | 后端日志 |
| 搜索响应时间 | < 300ms | 前端计时 |
| 图谱渲染时间 | < 500ms (100节点) | 前端计时 |
| 并发用户数 | 100+ | 压力测试 |
| 数据库查询 | < 100ms (P95) | 慢查询日志 |

### 3.2 安全要求

#### 3.2.1 认证与授权
- JWT Token认证，有效期7天
- 密码使用bcrypt加密（cost=12）
- 支持Token刷新机制
- 敏感操作需要二次验证

#### 3.2.2 数据安全
- 数据库连接使用SSL
- API通信使用HTTPS
- 敏感数据加密存储
- 定期安全审计

#### 3.2.3 防护措施
- SQL注入防护（使用ORM）
- XSS防护（输入验证 + 输出转义）
- CSRF防护（Token验证）
- 请求频率限制（100次/分钟）
- 文件上传验证（类型、大小、病毒扫描）

### 3.3 可用性要求

- **系统可用性**: 99.5% (允许每月停机3.6小时)
- **数据备份**: 每日自动备份，保留30天
- **灾难恢复**: RTO < 4小时，RPO < 1小时
- **错误处理**: 所有错误都有明确的提示信息
- **日志记录**: 记录所有关键操作和错误

### 3.4 兼容性要求

#### 3.4.1 浏览器支持
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

#### 3.4.2 数据库支持
- SQLite 3.35+ (开发/小型部署)
- PostgreSQL 12+ (生产环境推荐)
- MySQL 8.0+ (可选)

#### 3.4.3 部署环境
- Docker容器化部署
- Kubernetes集群部署
- 传统服务器部署
- 支持Linux、macOS、Windows

### 3.5 可扩展性要求

- **水平扩展**: 支持多实例部署
- **数据库扩展**: 支持读写分离、分库分表
- **缓存策略**: Redis缓存热点数据
- **CDN加速**: 静态资源使用CDN
- **插件系统**: 支持自定义导入适配器

### 3.6 可维护性要求

- **代码规范**: 遵循PEP8 (Python) 和ESLint (TypeScript)
- **文档完整**: API文档、部署文档、开发文档
- **测试覆盖**: 单元测试覆盖率 > 80%
- **日志规范**: 统一日志格式，分级记录
- **监控告警**: 关键指标监控，异常自动告警



---

## 4. 技术架构

### 4.1 技术栈选型

#### 4.1.1 前端技术栈
```
- 框架: React 18+
- 语言: TypeScript 4.9+
- 状态管理: Redux Toolkit
- UI组件: Ant Design 5.x
- 路由: React Router 6.x
- HTTP客户端: Axios
- WebSocket: Socket.io-client
- 图表: D3.js / ECharts
- Markdown编辑器: React-Markdown + CodeMirror
- 构建工具: Create React App / Vite
```

#### 4.1.2 后端技术栈
```
- 框架: FastAPI 0.100+
- 语言: Python 3.10+
- ORM: SQLAlchemy 2.0+
- 数据库迁移: Alembic
- 认证: JWT (python-jose)
- 密码加密: bcrypt
- 数据验证: Pydantic
- 异步任务: Celery (可选)
- WebSocket: FastAPI WebSocket
- 测试: pytest
```

#### 4.1.3 数据库与存储
```
- 关系数据库: PostgreSQL 12+ / SQLite 3.35+
- 缓存: Redis 6.0+ (可选)
- 文件存储: 本地文件系统 / S3兼容存储
- 全文搜索: PostgreSQL FTS / Elasticsearch (可选)
```

#### 4.1.4 部署与运维
```
- 容器化: Docker + Docker Compose
- 编排: Kubernetes (可选)
- Web服务器: Nginx
- 进程管理: Gunicorn / Uvicorn
- 监控: Prometheus + Grafana (可选)
- 日志: ELK Stack (可选)
```

### 4.2 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│  Web浏览器 (Chrome/Firefox/Safari/Edge)                 │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTPS
┌─────────────────────────────────────────────────────────┐
│                    前端应用层                            │
│  React SPA + Redux + Ant Design                         │
│  - 路由管理 (React Router)                              │
│  - 状态管理 (Redux Toolkit)                             │
│  - WebSocket连接 (Socket.io)                            │
└─────────────────────────────────────────────────────────┘
                          ↓ REST API / WebSocket
┌─────────────────────────────────────────────────────────┐
│                    API网关层                             │
│  Nginx (反向代理 + 负载均衡 + SSL终止)                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    后端应用层                            │
│  FastAPI + Uvicorn                                      │
│  ┌─────────────┬─────────────┬─────────────┐           │
│  │ API端点     │ WebSocket   │ 后台任务    │           │
│  │ (REST)      │ (实时通知)  │ (Celery)    │           │
│  └─────────────┴─────────────┴─────────────┘           │
│  ┌─────────────────────────────────────────┐           │
│  │         业务逻辑层 (Services)            │           │
│  │ - 认证服务 - 知识服务 - 图谱服务        │           │
│  │ - 搜索服务 - 导入服务 - 通知服务        │           │
│  └─────────────────────────────────────────┘           │
│  ┌─────────────────────────────────────────┐           │
│  │         数据访问层 (Models/ORM)          │           │
│  │ SQLAlchemy ORM + Alembic迁移             │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    数据存储层                            │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │ PostgreSQL   │ Redis        │ 文件系统     │        │
│  │ (主数据库)   │ (缓存/会话)  │ (附件存储)   │        │
│  └──────────────┴──────────────┴──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 4.3 数据库设计

#### 4.3.1 核心表结构

**用户表 (users)**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    bio TEXT,
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**知识表 (knowledge)**
```sql
CREATE TABLE knowledge (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(500),
    category_id UUID REFERENCES categories(id),
    is_public BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 全文搜索索引
    search_vector TSVECTOR
);

CREATE INDEX idx_knowledge_search ON knowledge USING GIN(search_vector);
CREATE INDEX idx_knowledge_category ON knowledge(category_id);
CREATE INDEX idx_knowledge_created_by ON knowledge(created_by);
```

**知识链接表 (knowledge_links)**
```sql
CREATE TABLE knowledge_links (
    id UUID PRIMARY KEY,
    from_item_id UUID REFERENCES knowledge(id) ON DELETE CASCADE,
    to_item_id UUID REFERENCES knowledge(id) ON DELETE CASCADE,
    link_type VARCHAR(20) NOT NULL,
    description VARCHAR(500),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- 防止重复链接
    UNIQUE(from_item_id, to_item_id, link_type)
);

CREATE INDEX idx_links_from ON knowledge_links(from_item_id);
CREATE INDEX idx_links_to ON knowledge_links(to_item_id);
```

**分类表 (categories)**
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    icon VARCHAR(50),
    color VARCHAR(20),
    sort_order INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**标签表 (tags)**
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(20),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 知识-标签关联表
CREATE TABLE knowledge_tags (
    knowledge_id UUID REFERENCES knowledge(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (knowledge_id, tag_id)
);
```

**通知表 (notifications)**
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    link VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
```



---

## 5. API接口规范

### 5.1 RESTful API设计原则

- 使用标准HTTP方法（GET、POST、PUT、DELETE）
- 使用复数名词表示资源（/api/v1/knowledge）
- 使用HTTP状态码表示结果
- 统一的错误响应格式
- 支持分页、排序、筛选
- API版本化（/api/v1/）

### 5.2 通用响应格式

#### 5.2.1 成功响应
```json
{
  "data": { ... },
  "message": "操作成功",
  "timestamp": "2026-02-10T12:00:00Z"
}
```

#### 5.2.2 分页响应
```json
{
  "items": [ ... ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

#### 5.2.3 错误响应
```json
{
  "detail": "错误描述",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ],
  "timestamp": "2026-02-10T12:00:00Z"
}
```

### 5.3 核心API端点

#### 5.3.1 认证相关
```
POST   /api/v1/auth/register      # 用户注册
POST   /api/v1/auth/login         # 用户登录
POST   /api/v1/auth/logout        # 用户登出
GET    /api/v1/auth/me            # 获取当前用户信息
POST   /api/v1/auth/refresh       # 刷新Token
POST   /api/v1/auth/reset-password # 重置密码
```

#### 5.3.2 知识管理
```
GET    /api/v1/knowledge          # 获取知识列表
POST   /api/v1/knowledge          # 创建知识
GET    /api/v1/knowledge/{id}     # 获取知识详情
PUT    /api/v1/knowledge/{id}     # 更新知识
DELETE /api/v1/knowledge/{id}     # 删除知识
GET    /api/v1/knowledge/{id}/versions  # 获取版本历史
POST   /api/v1/knowledge/{id}/restore   # 恢复到指定版本
```

#### 5.3.3 知识图谱
```
GET    /api/v1/knowledge-graph/links/{id}           # 获取知识链接
POST   /api/v1/knowledge-graph/links                # 创建链接
DELETE /api/v1/knowledge-graph/links/{id}           # 删除链接
GET    /api/v1/knowledge-graph/recommendations/{id} # 获取推荐
GET    /api/v1/knowledge-graph/stats                # 获取图谱统计
GET    /api/v1/knowledge-graph/graph                # 获取完整图谱数据
```

#### 5.3.4 搜索
```
GET    /api/v1/search             # 全文搜索
POST   /api/v1/search/advanced    # 高级搜索
GET    /api/v1/search/suggestions # 搜索建议
GET    /api/v1/search/history     # 搜索历史
```

#### 5.3.5 导入导出
```
POST   /api/v1/import/url         # URL导入
POST   /api/v1/import/markdown    # Markdown导入
POST   /api/v1/import/notion      # Notion导入
GET    /api/v1/export             # 数据导出
GET    /api/v1/export/{task_id}   # 获取导出任务状态
```

### 5.4 请求参数规范

#### 5.4.1 分页参数
```
page: 页码（从1开始）
page_size: 每页数量（默认20，最大100）
```

#### 5.4.2 排序参数
```
sort_by: 排序字段（created_at, updated_at, title等）
sort_order: 排序方向（asc, desc）
```

#### 5.4.3 筛选参数
```
category_id: 分类ID
tags: 标签列表（逗号分隔）
date_from: 开始日期（ISO 8601格式）
date_to: 结束日期（ISO 8601格式）
is_public: 是否公开（true/false）
```

### 5.5 HTTP状态码使用

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 验证失败 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器错误 |



---

## 6. 用户体验设计

### 6.1 界面布局

#### 6.1.1 整体布局
```
┌─────────────────────────────────────────────────────────┐
│  Header (顶部导航栏)                                     │
│  - Logo - 搜索框 - 通知 - 用户菜单                      │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│  Sidebar │         Main Content Area                   │
│          │         (主内容区域)                         │
│  - 仪表盘│                                              │
│  - 知识库│                                              │
│  - 图谱  │                                              │
│  - 分类  │                                              │
│  - 标签  │                                              │
│  - 导入  │                                              │
│  - 设置  │                                              │
│          │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

#### 6.1.2 响应式设计
- **桌面端** (>1200px): 侧边栏固定显示
- **平板端** (768px-1200px): 侧边栏可折叠
- **移动端** (<768px): 侧边栏抽屉式，底部导航栏

### 6.2 交互设计

#### 6.2.1 快捷键支持
```
Ctrl/Cmd + K     : 快速搜索
Ctrl/Cmd + N     : 新建知识
Ctrl/Cmd + S     : 保存
Ctrl/Cmd + /     : 显示快捷键帮助
Esc              : 关闭弹窗/取消操作
```

#### 6.2.2 拖拽操作
- 文件拖拽上传（Markdown、图片）
- 分类拖拽排序
- 知识拖拽移动分类

#### 6.2.3 右键菜单
- 知识列表：编辑、删除、移动、导出
- 分类树：新建子分类、重命名、删除
- 图谱节点：查看详情、编辑、添加链接

### 6.3 视觉设计

#### 6.3.1 色彩系统
```
主色调: #1890ff (蓝色 - 专业、可信)
成功色: #52c41a (绿色)
警告色: #faad14 (橙色)
错误色: #f5222d (红色)
中性色: #000000, #595959, #8c8c8c, #d9d9d9, #f0f0f0, #ffffff
```

#### 6.3.2 字体系统
```
标题字体: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
正文字体: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
代码字体: 'Fira Code', 'Consolas', 'Monaco', monospace

字号层级:
- H1: 32px (页面标题)
- H2: 24px (区块标题)
- H3: 20px (小标题)
- Body: 14px (正文)
- Small: 12px (辅助文字)
```

#### 6.3.3 间距系统
```
基础单位: 8px
间距层级: 4px, 8px, 16px, 24px, 32px, 48px, 64px
```

### 6.4 反馈机制

#### 6.4.1 加载状态
- 页面加载：骨架屏（Skeleton）
- 按钮操作：Loading图标
- 数据加载：进度条
- 长时间操作：进度百分比

#### 6.4.2 操作反馈
- 成功操作：绿色Toast提示（3秒自动消失）
- 失败操作：红色Toast提示（5秒自动消失）
- 警告信息：橙色Toast提示（4秒自动消失）
- 确认操作：Modal对话框

#### 6.4.3 空状态设计
- 无数据时显示友好的空状态插图
- 提供明确的操作指引
- 新用户显示引导教程

### 6.5 无障碍设计

- 支持键盘导航
- 合理的Tab顺序
- ARIA标签支持
- 高对比度模式
- 屏幕阅读器支持
- 字体大小可调节



---

## 7. 测试要求

### 7.1 测试策略

#### 7.1.1 测试金字塔
```
        /\
       /  \      E2E测试 (10%)
      /────\     - 关键用户流程
     /      \    - 端到端场景
    /────────\   
   /          \  集成测试 (30%)
  /────────────\ - API测试
 /              \- 数据库集成
/────────────────\
  单元测试 (60%)
  - 业务逻辑
  - 工具函数
```

### 7.2 单元测试

#### 7.2.1 后端单元测试
**覆盖范围**:
- 业务逻辑层（Services）
- 数据模型（Models）
- 工具函数（Utils）
- 验证器（Validators）

**测试框架**: pytest
**覆盖率要求**: > 80%

**示例测试用例**:
```python
def test_create_knowledge():
    """测试创建知识"""
    # Given: 准备测试数据
    data = {
        "title": "测试知识",
        "content": "测试内容"
    }
    
    # When: 执行创建操作
    knowledge = create_knowledge(data, user_id)
    
    # Then: 验证结果
    assert knowledge.title == "测试知识"
    assert knowledge.created_by == user_id
```

#### 7.2.2 前端单元测试
**覆盖范围**:
- React组件
- Redux reducers
- 工具函数
- 自定义Hooks

**测试框架**: Jest + React Testing Library
**覆盖率要求**: > 70%

### 7.3 集成测试

#### 7.3.1 API集成测试
**测试场景**:
- 认证流程（注册 → 登录 → 获取用户信息）
- 知识CRUD（创建 → 读取 → 更新 → 删除）
- 知识图谱（创建链接 → 获取链接 → 推荐 → 删除）
- 搜索功能（全文搜索 → 筛选 → 排序）

**测试脚本位置**: `tests/api/`

**示例**:
```python
def test_knowledge_workflow():
    """测试完整的知识管理流程"""
    # 1. 登录
    token = login("admin@admin.com", "admin12345")
    
    # 2. 创建知识
    knowledge = create_knowledge(token, {...})
    
    # 3. 更新知识
    updated = update_knowledge(token, knowledge.id, {...})
    
    # 4. 删除知识
    delete_knowledge(token, knowledge.id)
    
    # 5. 验证删除
    assert get_knowledge(token, knowledge.id) == 404
```

#### 7.3.2 数据库集成测试
**测试场景**:
- 数据库连接
- 事务处理
- 级联删除
- 约束验证

### 7.4 端到端测试

#### 7.4.1 关键用户流程
1. **新用户注册流程**
   - 访问注册页面
   - 填写注册信息
   - 提交注册
   - 验证邮箱
   - 登录系统

2. **知识创建与关联流程**
   - 登录系统
   - 创建新知识
   - 添加分类和标签
   - 创建知识链接
   - 查看知识图谱

3. **导入导出流程**
   - 导入URL内容
   - 编辑导入的知识
   - 导出为Markdown
   - 验证导出内容

**测试工具**: Playwright / Cypress
**测试频率**: 每次发布前

### 7.5 性能测试

#### 7.5.1 负载测试
**测试场景**:
- 100并发用户
- 1000次API请求/分钟
- 持续运行30分钟

**性能指标**:
- 响应时间 P95 < 200ms
- 错误率 < 0.1%
- CPU使用率 < 70%
- 内存使用率 < 80%

**测试工具**: Locust / JMeter

#### 7.5.2 压力测试
**测试目标**: 找到系统瓶颈
**测试方法**: 逐步增加并发用户数，直到系统崩溃

### 7.6 安全测试

#### 7.6.1 安全扫描
- SQL注入测试
- XSS攻击测试
- CSRF攻击测试
- 文件上传漏洞测试
- 权限绕过测试

**测试工具**: OWASP ZAP / Burp Suite

#### 7.6.2 依赖安全检查
```bash
# Python依赖检查
pip-audit

# Node.js依赖检查
npm audit
```

### 7.7 验收测试

#### 7.7.1 功能验收清单
- [ ] 所有功能按需求实现
- [ ] 所有API测试通过
- [ ] 前端页面正常显示
- [ ] 无明显Bug
- [ ] 性能指标达标

#### 7.7.2 用户验收测试（UAT）
- 邀请真实用户测试
- 收集用户反馈
- 修复关键问题
- 再次验收



---

## 8. 部署与运维

### 8.1 部署方案

#### 8.1.1 Docker部署（推荐）
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    image: knowledge-platform-backend:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/knowledge
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  frontend:
    image: knowledge-platform-frontend:latest
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=knowledge
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 8.1.2 Kubernetes部署
**资源配置**:
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: knowledge-backend
  template:
    metadata:
      labels:
        app: knowledge-backend
    spec:
      containers:
      - name: backend
        image: knowledge-platform-backend:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: knowledge-secrets
              key: database-url
```

#### 8.1.3 传统部署
**系统要求**:
- OS: Ubuntu 20.04+ / CentOS 8+
- Python: 3.10+
- Node.js: 16+
- PostgreSQL: 12+
- Nginx: 1.18+

**部署步骤**:
```bash
# 1. 安装依赖
sudo apt update
sudo apt install python3.10 nodejs npm postgresql nginx

# 2. 部署后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 部署前端
cd frontend
npm install
npm run build
sudo cp -r build/* /var/www/html/

# 4. 配置Nginx
sudo cp nginx.conf /etc/nginx/sites-available/knowledge
sudo ln -s /etc/nginx/sites-available/knowledge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8.2 环境配置

#### 8.2.1 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/knowledge
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080  # 7天

# 文件上传配置
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# CORS配置
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

#### 8.2.2 配置文件管理
- 开发环境: `.env.development`
- 测试环境: `.env.test`
- 生产环境: `.env.production`
- 敏感配置使用环境变量或密钥管理服务

### 8.3 监控与告警

#### 8.3.1 应用监控
**监控指标**:
- 请求量（QPS）
- 响应时间（P50, P95, P99）
- 错误率
- 活跃用户数
- 数据库连接数

**监控工具**: Prometheus + Grafana

**示例Prometheus配置**:
```yaml
scrape_configs:
  - job_name: 'knowledge-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

#### 8.3.2 日志管理
**日志级别**:
- DEBUG: 调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

**日志格式**:
```json
{
  "timestamp": "2026-02-10T12:00:00Z",
  "level": "INFO",
  "logger": "app.services.knowledge",
  "message": "Knowledge created",
  "user_id": "uuid",
  "knowledge_id": "uuid",
  "duration_ms": 45
}
```

**日志收集**: ELK Stack (Elasticsearch + Logstash + Kibana)

#### 8.3.3 告警规则
```yaml
# Prometheus告警规则
groups:
  - name: knowledge-platform
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "错误率过高"
          
      - alert: SlowResponse
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "响应时间过慢"
          
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes > 1073741824  # 1GB
        for: 5m
        annotations:
          summary: "内存使用过高"
```

### 8.4 备份与恢复

#### 8.4.1 数据库备份
**备份策略**:
- 全量备份: 每日凌晨2点
- 增量备份: 每小时
- 保留周期: 30天

**备份脚本**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups
DB_NAME=knowledge

# 全量备份
pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/full_$DATE.sql.gz

# 清理30天前的备份
find $BACKUP_DIR -name "full_*.sql.gz" -mtime +30 -delete
```

#### 8.4.2 文件备份
- 附件文件: 同步到对象存储（S3/OSS）
- 配置文件: 版本控制（Git）
- 日志文件: 归档到日志系统

#### 8.4.3 灾难恢复
**RTO (恢复时间目标)**: 4小时
**RPO (恢复点目标)**: 1小时

**恢复步骤**:
1. 准备新的服务器环境
2. 恢复最新的数据库备份
3. 恢复附件文件
4. 恢复配置文件
5. 启动服务
6. 验证功能正常

### 8.5 扩展方案

#### 8.5.1 水平扩展
- 后端服务: 多实例 + 负载均衡
- 数据库: 读写分离 + 主从复制
- 缓存: Redis集群
- 文件存储: 对象存储 + CDN

#### 8.5.2 垂直扩展
- 增加服务器CPU和内存
- 升级数据库配置
- 优化数据库索引
- 代码性能优化



---

## 9. 项目管理

### 9.1 开发流程

#### 9.1.1 Git工作流
```
main (生产分支)
  ↑
  merge
  ↑
develop (开发分支)
  ↑
  merge
  ↑
feature/xxx (功能分支)
```

**分支命名规范**:
- `feature/知识图谱` - 新功能
- `bugfix/修复搜索` - Bug修复
- `hotfix/紧急修复` - 紧急修复
- `refactor/重构代码` - 代码重构

#### 9.1.2 提交规范
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例**:
```
feat(knowledge-graph): 实现双向链接功能

- 添加知识链接数据模型
- 实现链接CRUD API
- 添加前端关联知识组件

Closes #123
```

#### 9.1.3 代码审查
- 所有代码必须经过Code Review
- 至少1人审查通过才能合并
- 审查重点：
  - 代码质量和规范
  - 功能实现正确性
  - 测试覆盖率
  - 性能影响
  - 安全问题

### 9.2 版本管理

#### 9.2.1 版本号规范
遵循语义化版本（Semantic Versioning）:
```
主版本号.次版本号.修订号

例如: v1.2.0
- 1: 主版本号（重大变更）
- 2: 次版本号（新功能）
- 0: 修订号（Bug修复）
```

#### 9.2.2 发布流程
1. 创建发布分支 `release/v1.2.0`
2. 更新版本号和CHANGELOG
3. 运行完整测试套件
4. 合并到main分支
5. 打标签 `git tag v1.2.0`
6. 部署到生产环境
7. 创建GitHub Release

### 9.3 文档管理

#### 9.3.1 文档类型
- **产品文档**: PRD、用户手册、FAQ
- **技术文档**: API文档、架构设计、数据库设计
- **开发文档**: 开发指南、代码规范、部署指南
- **运维文档**: 监控告警、故障处理、备份恢复

#### 9.3.2 文档更新
- 功能开发时同步更新文档
- 每次发布前检查文档完整性
- 文档使用Markdown格式
- 文档存放在 `docs/` 目录

### 9.4 质量保证

#### 9.4.1 代码质量
- 代码覆盖率 > 80%
- 无严重的代码异味
- 遵循代码规范
- 通过静态代码分析

**工具**:
- Python: pylint, black, mypy
- TypeScript: ESLint, Prettier
- SonarQube: 代码质量分析

#### 9.4.2 性能基准
- API响应时间 < 200ms (P95)
- 页面加载时间 < 2秒
- 搜索响应时间 < 300ms
- 图谱渲染时间 < 500ms

#### 9.4.3 安全基准
- 无高危漏洞
- 依赖包无已知漏洞
- 通过安全扫描
- 定期安全审计

---

## 10. 风险管理

### 10.1 技术风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 数据库性能瓶颈 | 高 | 中 | 读写分离、缓存优化、索引优化 |
| 第三方API不稳定 | 中 | 中 | 重试机制、降级方案、备用方案 |
| 并发冲突 | 中 | 低 | 乐观锁、版本控制、冲突检测 |
| 数据丢失 | 高 | 低 | 定期备份、主从复制、灾备方案 |

### 10.2 业务风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 用户需求变更 | 中 | 高 | 敏捷开发、快速迭代、需求管理 |
| 竞品压力 | 中 | 中 | 差异化功能、用户体验优化 |
| 数据安全问题 | 高 | 低 | 安全审计、权限控制、加密存储 |
| 性能问题投诉 | 中 | 中 | 性能监控、优化迭代、用户反馈 |

### 10.3 项目风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 开发进度延期 | 中 | 中 | 合理排期、风险缓冲、资源调配 |
| 人员流动 | 中 | 低 | 知识沉淀、文档完善、交接机制 |
| 技术债务累积 | 中 | 中 | 定期重构、代码审查、技术规范 |
| 测试不充分 | 高 | 中 | 自动化测试、测试覆盖率、QA流程 |

---

## 11. 附录

### 11.1 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 知识图谱 | Knowledge Graph | 知识之间的关系网络 |
| 双向链接 | Bidirectional Link | 知识之间的相互引用关系 |
| 前置知识 | Prerequisite | 学习当前知识前需要掌握的知识 |
| 衍生知识 | Derived | 从当前知识延伸出的知识 |
| 孤立节点 | Isolated Node | 没有任何链接的知识 |
| 全文搜索 | Full-Text Search | 在标题和内容中搜索关键词 |
| 适配器模式 | Adapter Pattern | 用于集成不同数据源的设计模式 |

### 11.2 参考资料

**产品参考**:
- Notion: https://www.notion.so
- Obsidian: https://obsidian.md
- Roam Research: https://roamresearch.com

**技术文档**:
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- PostgreSQL: https://www.postgresql.org/docs
- D3.js: https://d3js.org

**设计规范**:
- Ant Design: https://ant.design
- Material Design: https://material.io

### 11.3 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-02-10 | 初始版本，基于v1.2.0实现整理 | Kiro AI |

---

## 12. 总结与建议

### 12.1 为什么这份PRD很重要？

通过我们的实际开发过程，我深刻体会到：

1. **明确的需求减少返工**
   - 我们在开发过程中多次修改API路径、字段名、错误处理
   - 如果一开始就有明确的接口规范，这些问题可以避免

2. **完整的技术规范提高效率**
   - 数据库字段名统一（`from_item_id` vs `source_id`）
   - API响应格式统一（`items` vs `results`）
   - 错误处理格式统一

3. **详细的验收标准保证质量**
   - 每个功能都有明确的验收标准
   - 测试用例可以直接从验收标准转化
   - 减少功能遗漏和理解偏差

### 12.2 如何使用这份PRD？

**对于产品经理**:
- 作为需求沟通的基础文档
- 作为功能验收的标准
- 作为项目进度的参考

**对于开发人员**:
- 作为开发的详细指南
- 作为技术选型的参考
- 作为接口设计的规范

**对于测试人员**:
- 作为测试用例的来源
- 作为验收测试的标准
- 作为性能测试的基准

**对于运维人员**:
- 作为部署的指导文档
- 作为监控的配置参考
- 作为故障处理的手册

### 12.3 持续改进

这份PRD应该是一个活文档：
- 随着产品迭代不断更新
- 收集用户反馈持续优化
- 记录技术决策和经验教训
- 作为团队知识沉淀的载体

---

**文档结束**

如有疑问或建议，请联系项目团队。

