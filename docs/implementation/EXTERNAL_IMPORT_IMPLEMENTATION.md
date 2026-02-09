# 外部平台导入功能实现文档

## 概述

本文档描述外部平台导入适配器的实现，支持从CSDN、微信公众号、Notion等平台导入内容。

---

## 已实现的适配器

### 1. CSDN适配器 (`CSDNAdapter`)

#### 功能特性
- 从CSDN博客抓取文章列表
- 解析文章内容（标题、正文、标签）
- HTML转Markdown
- 自动提取文章ID

#### 配置要求
```python
{
    "username": "csdn_username"  # CSDN用户名
}
```

#### 使用示例
```python
from app.services.adapters import CSDNAdapter

config = {"username": "your_username"}
adapter = CSDNAdapter(config)

# 验证配置
is_valid = await adapter.validate_config()

# 导入文章
items = await adapter.import_items(limit=10)
```

#### 数据转换
- **标题**: 直接提取
- **内容**: HTML转Markdown
- **标签**: 提取文章标签
- **分类**: 自动设置为"CSDN导入"
- **来源**: 记录原文URL和文章ID

#### 注意事项
- 需要处理CSDN的反爬虫机制
- 建议添加请求延迟和User-Agent
- 大量抓取时注意速率限制

---

### 2. 微信公众号适配器 (`WeChatAdapter`)

#### 功能特性
- 通过微信公众平台API获取文章
- 支持OAuth认证
- 批量获取文章列表
- 保留原文格式和图片

#### 配置要求
```python
{
    "app_id": "your_app_id",        # 公众号AppID
    "app_secret": "your_app_secret"  # 公众号AppSecret
}
```

#### 使用示例
```python
from app.services.adapters import WeChatAdapter

config = {
    "app_id": "wx1234567890",
    "app_secret": "secret_key"
}
adapter = WeChatAdapter(config)

# 导入文章
items = await adapter.import_items(limit=20)
```

#### 数据转换
- **标题**: 直接提取
- **内容**: HTML转Markdown
- **摘要**: 使用文章摘要
- **标签**: 自动添加"微信公众号"
- **分类**: 自动设置为"微信公众号导入"
- **元数据**: 保存作者、封面图等信息

#### API要求
1. 注册微信公众平台开发者账号
2. 创建公众号应用
3. 获取AppID和AppSecret
4. 配置服务器白名单

#### 注意事项
- Access Token有效期2小时，需要刷新
- API调用有频率限制
- 需要公众号认证才能使用部分接口

---

### 3. Notion适配器 (`NotionAdapter`)

#### 功能特性
- 通过Notion API获取页面
- 支持数据库查询
- 块级内容解析
- Notion格式转Markdown

#### 配置要求
```python
{
    "api_key": "secret_xxx",           # Notion Integration API Key
    "database_id": "xxx" (可选)        # 特定数据库ID
}
```

#### 使用示例
```python
from app.services.adapters import NotionAdapter

config = {
    "api_key": "secret_abc123",
    "database_id": "database_id_here"  # 可选
}
adapter = NotionAdapter(config)

# 导入页面
items = await adapter.import_items(limit=50)
```

#### 数据转换
- **标题**: 从title属性提取
- **内容**: Notion块转Markdown
- **标签**: 从multi_select属性提取
- **分类**: 自动设置为"Notion导入"
- **元数据**: 保存Notion ID、父页面等信息

#### 支持的Notion块类型
- Paragraph（段落）
- Heading 1/2/3（标题）
- Bulleted List（无序列表）
- Numbered List（有序列表）
- Code（代码块）
- 更多块类型可扩展

#### API设置步骤
1. 访问 https://www.notion.so/my-integrations
2. 创建新的Integration
3. 获取Internal Integration Token
4. 在Notion页面中添加Integration权限

#### 注意事项
- API版本：2022-06-28
- 需要为Integration授予页面访问权限
- 支持分页查询大量数据

---

## 适配器架构

### 基类 (`BaseAdapter`)

所有适配器继承自`BaseAdapter`，提供统一接口：

```python
class BaseAdapter(ABC):
    @abstractmethod
    async def validate_config(self) -> bool:
        """验证配置"""
        pass
    
    @abstractmethod
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取原始数据"""
        pass
    
    @abstractmethod
    async def transform_item(
        self,
        raw_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """转换为标准格式"""
        pass
    
    async def import_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """完整导入流程"""
        pass
```

### 标准数据格式

所有适配器转换后的数据格式：

```python
{
    "title": str,                    # 标题
    "content": str,                  # 内容（Markdown）
    "content_type": str,             # 内容类型
    "summary": Optional[str],        # 摘要
    "tags": List[str],               # 标签列表
    "category": Optional[str],       # 分类
    "source_platform": str,          # 来源平台
    "source_url": Optional[str],     # 原文URL
    "source_id": str,                # 原文ID
    "published_at": Optional[datetime],  # 发布时间
    "meta_data": Dict[str, Any]      # 元数据
}
```

---

## 使用导入引擎

### 注册适配器

```python
from app.services.import_engine import ImportEngine

# 适配器已自动注册
ImportEngine.ADAPTERS = {
    'markdown': MarkdownAdapter,
    'csdn': CSDNAdapter,
    'wechat': WeChatAdapter,
    'notion': NotionAdapter,
}
```

### 创建导入任务

```python
from app.services.import_engine import ImportEngine

engine = ImportEngine(db)

# 创建导入配置
config_data = {
    "name": "我的CSDN博客",
    "platform": "csdn",
    "config": {
        "username": "my_username"
    },
    "auto_sync": True,
    "sync_interval": 3600
}

config = await engine.create_import_config(user_id, config_data)

# 执行导入
result = await engine.execute_import(config.id, user_id)
```

---

## 扩展新适配器

### 步骤

1. **创建适配器类**
```python
from app.services.adapters.base import BaseAdapter

class MyPlatformAdapter(BaseAdapter):
    async def validate_config(self) -> bool:
        # 验证配置
        pass
    
    async def fetch_items(self, since, limit):
        # 获取数据
        pass
    
    async def transform_item(self, raw_item):
        # 转换数据
        pass
```

2. **注册适配器**
```python
# 在 import_engine.py 中添加
ImportEngine.ADAPTERS['myplatform'] = MyPlatformAdapter
```

3. **测试适配器**
```python
config = {"key": "value"}
adapter = MyPlatformAdapter(config)
items = await adapter.import_items(limit=10)
```

---

## 安全考虑

### API密钥管理
- 使用环境变量存储敏感信息
- 加密存储在数据库中的配置
- 定期轮换API密钥

### 速率限制
- 实现请求延迟
- 遵守平台API限制
- 使用指数退避重试

### 数据验证
- 验证导入的内容格式
- 过滤恶意内容
- 检查文件大小限制

---

## 错误处理

### 常见错误

1. **配置错误**
   - 缺少必需字段
   - API密钥无效
   - 权限不足

2. **网络错误**
   - 连接超时
   - API不可用
   - 速率限制

3. **数据错误**
   - 内容格式不正确
   - 缺少必需字段
   - 编码问题

### 处理策略
- 记录详细错误日志
- 提供友好的错误消息
- 支持部分导入（跳过错误项）
- 提供重试机制

---

## 性能优化

### 批量处理
- 批量获取数据
- 批量插入数据库
- 使用事务

### 异步处理
- 使用异步HTTP请求
- 并发处理多个项目
- 后台任务队列

### 缓存
- 缓存API响应
- 缓存转换结果
- 避免重复导入

---

## 测试

### 单元测试
```python
async def test_csdn_adapter():
    config = {"username": "test_user"}
    adapter = CSDNAdapter(config)
    
    assert await adapter.validate_config()
    
    items = await adapter.fetch_items(limit=1)
    assert len(items) > 0
    
    transformed = await adapter.transform_item(items[0])
    assert 'title' in transformed
    assert 'content' in transformed
```

### 集成测试
- 测试完整导入流程
- 测试错误处理
- 测试数据一致性

---

## 未来改进

### 短期
1. 添加更多平台适配器（知乎、简书等）
2. 改进HTML到Markdown转换
3. 支持图片下载和存储
4. 添加导入进度显示

### 中期
1. 实现增量同步
2. 支持双向同步
3. 添加冲突解决机制
4. 优化大批量导入性能

### 长期
1. AI辅助内容分类
2. 自动标签提取
3. 内容去重和合并
4. 智能内容推荐

---

## 依赖

### Python包
```
aiohttp>=3.8.0      # 异步HTTP客户端
beautifulsoup4>=4.11.0  # HTML解析
lxml>=4.9.0         # XML/HTML解析器
```

### 安装
```bash
pip install aiohttp beautifulsoup4 lxml
```

---

## 参考资料

### API文档
- [微信公众平台API](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)
- [Notion API](https://developers.notion.com/)
- [CSDN博客](https://blog.csdn.net/)

### 相关标准
- [Markdown规范](https://commonmark.org/)
- [HTML5规范](https://html.spec.whatwg.org/)

---

**当前状态**: ✅ 基础适配器已实现，可扩展

**下一步**: 添加API端点和前端界面

