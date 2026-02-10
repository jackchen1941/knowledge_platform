# 多设备同步和多平台导入使用指南

## 目录
1. [多设备同步管理](#多设备同步管理)
2. [多平台导入功能](#多平台导入功能)
3. [支持的平台](#支持的平台)
4. [通过URL导入文章](#通过url导入文章)
5. [API使用示例](#api使用示例)

---

## 多设备同步管理

### 功能概述
多设备同步功能允许你在多个设备（手机、平板、电脑等）之间同步知识库数据，确保所有设备上的数据保持一致。

### 核心功能
- ✅ 设备注册和管理
- ✅ 增量同步（只同步变更的数据）
- ✅ 冲突检测和解决
- ✅ 同步日志和统计
- ✅ 离线支持（本地缓存）

### 使用步骤

#### 1. 注册设备

每个设备在首次使用时需要注册：

```bash
# API请求
POST /api/v1/sync/devices/register
Authorization: Bearer {your_token}

{
  "device_name": "我的iPhone",
  "device_type": "mobile",  # mobile, desktop, web
  "device_id": "unique-device-identifier"  # 设备唯一标识
}
```

**设备类型说明**:
- `mobile`: 手机端
- `desktop`: 桌面端
- `web`: 网页端

**设备ID生成建议**:
- iOS: 使用 `identifierForVendor`
- Android: 使用 `ANDROID_ID`
- Web: 使用浏览器指纹或生成UUID并存储在localStorage
- Desktop: 使用机器MAC地址或生成UUID

#### 2. 查看已注册设备

```bash
GET /api/v1/sync/devices
Authorization: Bearer {your_token}
```

响应示例：
```json
[
  {
    "id": "device-uuid-1",
    "device_name": "我的iPhone",
    "device_type": "mobile",
    "device_id": "ios-device-123",
    "last_sync": "2026-02-10T10:30:00Z",
    "is_active": true,
    "created_at": "2026-02-01T08:00:00Z"
  },
  {
    "id": "device-uuid-2",
    "device_name": "工作电脑",
    "device_type": "desktop",
    "device_id": "mac-device-456",
    "last_sync": "2026-02-10T09:15:00Z",
    "is_active": true,
    "created_at": "2026-02-05T14:30:00Z"
  }
]
```

#### 3. 拉取更新（Pull）

从服务器获取其他设备的更新：

```bash
POST /api/v1/sync/pull
Authorization: Bearer {your_token}

{
  "device_id": "device-uuid-1",
  "last_sync": "2026-02-10T09:00:00Z"  # 可选，上次同步时间
}
```

响应示例：
```json
{
  "changes": {
    "knowledge": [
      {
        "id": "knowledge-id-1",
        "operation": "create",
        "data": {
          "title": "新文章",
          "content": "文章内容...",
          "created_at": "2026-02-10T10:00:00Z"
        },
        "timestamp": "2026-02-10T10:00:00Z"
      },
      {
        "id": "knowledge-id-2",
        "operation": "update",
        "data": {
          "title": "更新的标题",
          "updated_at": "2026-02-10T10:15:00Z"
        },
        "timestamp": "2026-02-10T10:15:00Z"
      }
    ],
    "categories": [],
    "tags": []
  },
  "sync_time": "2026-02-10T10:30:00Z",
  "has_conflicts": false
}
```

#### 4. 推送更新（Push）

将本地更改推送到服务器：

```bash
POST /api/v1/sync/push
Authorization: Bearer {your_token}

{
  "device_id": "device-uuid-1",
  "changes": [
    {
      "entity_type": "knowledge",
      "entity_id": "knowledge-id-3",
      "operation": "create",
      "timestamp": "2026-02-10T10:20:00Z",
      "data": {
        "title": "本地创建的文章",
        "content": "内容...",
        "is_published": true
      }
    }
  ]
}
```

响应示例：
```json
{
  "applied": 1,
  "conflicts": 0,
  "errors": [],
  "sync_time": "2026-02-10T10:30:00Z"
}
```

#### 5. 处理冲突

当多个设备同时修改同一条数据时，会产生冲突：

```bash
# 查看冲突列表
GET /api/v1/sync/conflicts
Authorization: Bearer {your_token}
```

响应示例：
```json
[
  {
    "id": "conflict-id-1",
    "entity_type": "knowledge",
    "entity_id": "knowledge-id-1",
    "device1_id": "device-uuid-1",
    "device2_id": "device-uuid-2",
    "device1_data": {
      "title": "版本A",
      "updated_at": "2026-02-10T10:00:00Z"
    },
    "device2_data": {
      "title": "版本B",
      "updated_at": "2026-02-10T10:05:00Z"
    },
    "resolved": false,
    "created_at": "2026-02-10T10:10:00Z"
  }
]
```

解决冲突：
```bash
POST /api/v1/sync/conflicts/{conflict_id}/resolve
Authorization: Bearer {your_token}

{
  "resolution": "device1"  # device1, device2, merge, manual
}
```

#### 6. 停用设备

```bash
DELETE /api/v1/sync/devices/{device_id}
Authorization: Bearer {your_token}
```

### 同步策略建议

1. **自动同步**: 应用启动时自动执行一次完整同步
2. **定时同步**: 每15-30分钟执行一次增量同步
3. **实时同步**: 使用WebSocket接收实时更新通知
4. **离线支持**: 本地缓存所有数据，离线时可正常使用
5. **冲突处理**: 优先使用"最后修改时间"策略，复杂冲突提示用户手动选择

---

## 多平台导入功能

### 功能概述
支持从多个外部平台导入文章和内容，包括公开访问的文档链接。

### 核心功能
- ✅ 多平台适配器架构
- ✅ 通过URL直接导入
- ✅ 批量导入
- ✅ 增量导入（只导入新内容）
- ✅ 自动格式转换（HTML → Markdown）
- ✅ 元数据保留

---

## 支持的平台

### 1. CSDN博客 ✅

**配置要求**:
```json
{
  "username": "your-csdn-username"
}
```

**支持的导入方式**:
- 通过用户名导入所有文章
- 通过文章URL导入单篇文章

**示例URL**:
```
https://blog.csdn.net/username/article/details/123456789
```

### 2. 微信公众号 ✅

**配置要求**:
```json
{
  "app_id": "your-app-id",
  "app_secret": "your-app-secret"
}
```

**注意事项**:
- 需要注册微信公众号开发者账号
- 需要获取API访问权限
- 支持导入公众号历史文章

**获取配置步骤**:
1. 登录微信公众平台 (https://mp.weixin.qq.com)
2. 进入"开发" → "基本配置"
3. 获取AppID和AppSecret

### 3. Notion ✅

**配置要求**:
```json
{
  "api_key": "your-notion-api-key",
  "database_id": "your-database-id"  # 可选
}
```

**支持的导入方式**:
- 导入整个数据库
- 导入单个页面
- 支持嵌套页面

**获取配置步骤**:
1. 访问 https://www.notion.so/my-integrations
2. 创建新的集成（Integration）
3. 复制Internal Integration Token
4. 在Notion页面中分享给你的集成

### 4. Markdown文件 ✅

**配置要求**:
```json
{
  "file_path": "/path/to/file.md"
}
```

**支持的导入方式**:
- 单个Markdown文件
- 文件夹批量导入
- 支持Front Matter元数据

### 5. 通用URL导入 ✅ (推荐)

**适用场景**: 任何公开访问的网页文章

**支持的网站类型**:
- 博客文章
- 技术文档
- 新闻文章
- 知乎文章
- 简书文章
- 掘金文章
- 小红书笔记（公开）
- Medium文章
- 等等...

**配置要求**:
```json
{
  "url": "https://example.com/article/123"
}
```

---

## 通过URL导入文章

### 方法1: 使用通用URL导入适配器

这是最简单和推荐的方法，适用于大多数公开网页。

#### 步骤1: 创建导入配置

```bash
POST /api/v1/import-adapters/configs
Authorization: Bearer {your_token}

{
  "platform": "url",
  "name": "通用URL导入",
  "config": {
    "url": "https://example.com/article/123"
  }
}
```

#### 步骤2: 测试连接

```bash
POST /api/v1/import-adapters/configs/{config_id}/test
Authorization: Bearer {your_token}
```

#### 步骤3: 开始导入

```bash
POST /api/v1/import-adapters/configs/{config_id}/import
Authorization: Bearer {your_token}

{
  "incremental": false  # false=全量导入, true=增量导入
}
```

### 方法2: 直接通过URL导入（快捷方式）

```bash
POST /api/v1/import-adapters/import-url
Authorization: Bearer {your_token}

{
  "url": "https://example.com/article/123",
  "category": "技术文章",  # 可选
  "tags": ["Python", "教程"]  # 可选
}
```

响应示例：
```json
{
  "success": true,
  "knowledge_id": "knowledge-uuid-123",
  "title": "文章标题",
  "imported_at": "2026-02-10T10:30:00Z",
  "metadata": {
    "word_count": 1500,
    "reading_time": 8,
    "source_url": "https://example.com/article/123"
  }
}
```

### 支持的URL格式示例

```bash
# CSDN
https://blog.csdn.net/username/article/details/123456789

# 知乎
https://zhuanlan.zhihu.com/p/123456789

# 简书
https://www.jianshu.com/p/abc123def456

# 掘金
https://juejin.cn/post/7123456789012345678

# 小红书（公开笔记）
https://www.xiaohongshu.com/explore/123456789abc

# Medium
https://medium.com/@username/article-title-123abc

# GitHub README
https://github.com/username/repo/blob/main/README.md

# 个人博客
https://yourblog.com/posts/article-title
```

### URL导入的工作原理

1. **内容抓取**: 使用HTTP请求获取网页HTML
2. **内容提取**: 
   - 使用BeautifulSoup解析HTML
   - 智能识别文章标题、正文、作者等
   - 过滤广告、导航栏等无关内容
3. **格式转换**: 
   - HTML → Markdown
   - 保留图片、代码块、列表等格式
4. **元数据提取**:
   - 标题、作者、发布时间
   - 标签、分类
   - 原文链接
5. **保存到知识库**:
   - 创建新的知识条目
   - 关联分类和标签
   - 记录来源信息

---

## API使用示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your-access-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. 注册设备
def register_device():
    response = requests.post(
        f"{BASE_URL}/sync/devices/register",
        headers=headers,
        json={
            "device_name": "我的电脑",
            "device_type": "desktop",
            "device_id": "mac-12345"
        }
    )
    return response.json()

# 2. 通过URL导入文章
def import_from_url(url):
    response = requests.post(
        f"{BASE_URL}/import-adapters/import-url",
        headers=headers,
        json={
            "url": url,
            "category": "技术文章",
            "tags": ["Python", "教程"]
        }
    )
    return response.json()

# 3. 同步数据
def sync_pull(device_id, last_sync=None):
    response = requests.post(
        f"{BASE_URL}/sync/pull",
        headers=headers,
        json={
            "device_id": device_id,
            "last_sync": last_sync
        }
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 注册设备
    device = register_device()
    print(f"设备已注册: {device['device_name']}")
    
    # 导入文章
    result = import_from_url("https://blog.csdn.net/example/article/details/123456")
    print(f"文章已导入: {result['title']}")
    
    # 同步数据
    changes = sync_pull(device['id'])
    print(f"同步完成，获取到 {len(changes['changes']['knowledge'])} 条更新")
```

### JavaScript示例

```javascript
const BASE_URL = "http://localhost:8000/api/v1";
const TOKEN = "your-access-token";

const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// 1. 注册设备
async function registerDevice() {
  const response = await fetch(`${BASE_URL}/sync/devices/register`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
      device_name: "我的浏览器",
      device_type: "web",
      device_id: `web-${Date.now()}`
    })
  });
  return await response.json();
}

// 2. 通过URL导入文章
async function importFromUrl(url) {
  const response = await fetch(`${BASE_URL}/import-adapters/import-url`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
      url: url,
      category: "技术文章",
      tags: ["JavaScript", "教程"]
    })
  });
  return await response.json();
}

// 3. 同步数据
async function syncPull(deviceId, lastSync = null) {
  const response = await fetch(`${BASE_URL}/sync/pull`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
      device_id: deviceId,
      last_sync: lastSync
    })
  });
  return await response.json();
}

// 使用示例
(async () => {
  // 注册设备
  const device = await registerDevice();
  console.log(`设备已注册: ${device.device_name}`);
  
  // 导入文章
  const result = await importFromUrl("https://juejin.cn/post/7123456789");
  console.log(`文章已导入: ${result.title}`);
  
  // 同步数据
  const changes = await syncPull(device.id);
  console.log(`同步完成，获取到 ${changes.changes.knowledge.length} 条更新`);
})();
```

---

## 高级功能

### 1. 批量URL导入

```bash
POST /api/v1/import-adapters/import-urls
Authorization: Bearer {your_token}

{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
  ],
  "category": "技术文章",
  "tags": ["Python"]
}
```

### 2. 定时自动导入

创建定时任务配置：

```bash
POST /api/v1/import-adapters/configs
Authorization: Bearer {your_token}

{
  "platform": "csdn",
  "name": "CSDN自动导入",
  "config": {
    "username": "your-username"
  },
  "schedule": {
    "enabled": true,
    "interval": "daily",  # daily, weekly, hourly
    "time": "08:00"  # 每天8点执行
  }
}
```

### 3. 导入过滤规则

```bash
POST /api/v1/import-adapters/configs
Authorization: Bearer {your_token}

{
  "platform": "url",
  "name": "技术文章导入",
  "config": {
    "url_pattern": "https://blog.example.com/tech/*"
  },
  "filters": {
    "min_word_count": 500,  # 最少字数
    "exclude_keywords": ["广告", "推广"],  # 排除关键词
    "include_keywords": ["Python", "JavaScript"]  # 包含关键词
  }
}
```

---

## 常见问题

### Q1: 如何处理需要登录的网站？

A: 对于需要登录的网站，你需要：
1. 在配置中提供认证信息（用户名/密码或API Token）
2. 或者使用浏览器扩展导出Cookie
3. 或者使用平台提供的官方API

### Q2: 导入的文章格式不正确怎么办？

A: 系统会自动将HTML转换为Markdown，但某些复杂格式可能需要手动调整。你可以：
1. 导入后在编辑器中调整格式
2. 使用自定义的转换规则
3. 提交Issue让我们改进转换算法

### Q3: 如何避免重复导入？

A: 系统会根据`source_url`和`source_id`自动检测重复：
- 如果文章已存在，会更新而不是创建新的
- 可以在配置中设置`skip_existing: true`跳过已存在的文章

### Q4: 多设备同步会消耗很多流量吗？

A: 不会，因为：
1. 使用增量同步，只传输变更的数据
2. 支持压缩传输
3. 可以设置仅在WiFi下同步

### Q5: 同步冲突如何处理？

A: 系统提供多种冲突解决策略：
1. **自动**: 使用最后修改时间（默认）
2. **手动**: 提示用户选择保留哪个版本
3. **合并**: 尝试自动合并（适用于不同字段的修改）

---

## 下一步计划

### 即将支持的平台
- [ ] 语雀
- [ ] 飞书文档
- [ ] 石墨文档
- [ ] 印象笔记
- [ ] 有道云笔记
- [ ] Obsidian
- [ ] Logseq

### 功能增强
- [ ] 浏览器扩展（一键导入当前页面）
- [ ] 移动端App
- [ ] 离线优先架构
- [ ] 端到端加密
- [ ] 协作编辑

---

## 技术支持

如有问题，请：
1. 查看API文档: http://localhost:8000/docs
2. 查看日志: `backend/logs/app.log`
3. 提交Issue到GitHub仓库

