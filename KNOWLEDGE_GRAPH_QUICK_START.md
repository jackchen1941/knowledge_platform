# 🚀 知识图谱快速开始 / Knowledge Graph Quick Start

> 30分钟实现知识详情页的关联功能

## 📋 目标

在知识详情页添加"关联知识"功能，让用户可以：
- 查看当前知识的所有关联
- 添加新的关联
- 删除现有关联
- 查看智能推荐的相关知识

## 🎯 效果预览

```
┌─────────────────────────────────────────────────┐
│  知识详情                                        │
├─────────────────────────────────────────────────┤
│  标题: Python异步编程                            │
│  内容: ...                                       │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │  关联知识              [+ 添加关联]       │  │
│  ├───────────────────────────────────────────┤  │
│  │  → Python协程详解 (前置知识)    [删除]   │  │
│  │  → asyncio库使用指南 (相关)     [删除]   │  │
│  │  ← FastAPI异步实践 (衍生)       [删除]   │  │
│  ├───────────────────────────────────────────┤  │
│  │  💡 推荐关联                              │  │
│  │  • Python多线程编程 (相似度: 85) [添加]  │  │
│  │  • 异步IO原理 (相似度: 78)       [添加]  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 📝 实施步骤

### 步骤 1: 创建关联知识组件 (15分钟)

创建文件: `frontend/src/components/knowledge/RelatedKnowledgeSection.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Button,
  Tag,
  Modal,
  Select,
  Input,
  message,
  Space,
  Divider,
  Empty,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  LinkOutlined,
  ArrowRightOutlined,
  ArrowLeftOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import api from '@/services/api';

interface Link {
  id: string;
  source_id: string;
  target_id: string;
  link_type: string;
  description: string | null;
  target_title?: string;
  source_title?: string;
}

interface Suggestion {
  id: string;
  title: string;
  score: number;
  reasons: string[];
  category: string | null;
  tags: Array<{ name: string; color: string }>;
}

interface RelatedKnowledgeSectionProps {
  knowledgeId: string;
}

const LINK_TYPES = {
  related: { label: '相关', color: 'blue' },
  prerequisite: { label: '前置知识', color: 'orange' },
  derived: { label: '衍生', color: 'green' },
  similar: { label: '相似', color: 'cyan' },
  reference: { label: '引用', color: 'purple' },
};

const RelatedKnowledgeSection: React.FC<RelatedKnowledgeSectionProps> = ({
  knowledgeId,
}) => {
  const [loading, setLoading] = useState(false);
  const [outgoingLinks, setOutgoingLinks] = useState<Link[]>([]);
  const [incomingLinks, setIncomingLinks] = useState<Link[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedKnowledge, setSelectedKnowledge] = useState<string | null>(null);
  const [selectedLinkType, setSelectedLinkType] = useState('related');

  useEffect(() => {
    loadLinks();
    loadSuggestions();
  }, [knowledgeId]);

  const loadLinks = async () => {
    setLoading(true);
    try {
      // 获取outgoing链接
      const outgoingRes = await api.get(
        `/api/v1/knowledge/${knowledgeId}/links?direction=outgoing`
      );
      setOutgoingLinks(outgoingRes.data);

      // 获取incoming链接
      const incomingRes = await api.get(
        `/api/v1/knowledge/${knowledgeId}/links?direction=incoming`
      );
      setIncomingLinks(incomingRes.data);
    } catch (error) {
      message.error('加载关联知识失败');
    } finally {
      setLoading(false);
    }
  };

  const loadSuggestions = async () => {
    try {
      const res = await api.get(`/api/v1/knowledge/${knowledgeId}/related?limit=5`);
      setSuggestions(res.data.suggestions || []);
    } catch (error) {
      console.error('加载推荐失败', error);
    }
  };

  const searchKnowledge = async (keyword: string) => {
    if (!keyword.trim()) {
      setSearchResults([]);
      return;
    }

    setSearchLoading(true);
    try {
      const res = await api.get(`/api/v1/search?q=${encodeURIComponent(keyword)}`);
      // 过滤掉当前知识
      const filtered = res.data.results.filter((item: any) => item.id !== knowledgeId);
      setSearchResults(filtered);
    } catch (error) {
      message.error('搜索失败');
    } finally {
      setSearchLoading(false);
    }
  };

  const createLink = async (targetId: string, linkType: string) => {
    try {
      await api.post(`/api/v1/knowledge/${knowledgeId}/links`, {
        target_id: targetId,
        link_type: linkType,
      });
      message.success('关联创建成功');
      loadLinks();
      loadSuggestions();
      setModalVisible(false);
      setSelectedKnowledge(null);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建关联失败');
    }
  };

  const deleteLink = async (linkId: string) => {
    try {
      await api.delete(`/api/v1/links/${linkId}`);
      message.success('关联已删除');
      loadLinks();
      loadSuggestions();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const renderLinkItem = (link: Link, direction: 'outgoing' | 'incoming') => {
    const isOutgoing = direction === 'outgoing';
    const title = isOutgoing ? link.target_title : link.source_title;
    const targetId = isOutgoing ? link.target_id : link.source_id;
    const linkTypeInfo = LINK_TYPES[link.link_type as keyof typeof LINK_TYPES] || {
      label: link.link_type,
      color: 'default',
    };

    return (
      <List.Item
        actions={[
          <Button
            type="link"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => deleteLink(link.id)}
          >
            删除
          </Button>,
        ]}
      >
        <List.Item.Meta
          avatar={
            isOutgoing ? (
              <ArrowRightOutlined style={{ fontSize: 16, color: '#1890ff' }} />
            ) : (
              <ArrowLeftOutlined style={{ fontSize: 16, color: '#52c41a' }} />
            )
          }
          title={
            <a href={`/knowledge/${targetId}`} target="_blank" rel="noopener noreferrer">
              {title}
            </a>
          }
          description={
            <Space>
              <Tag color={linkTypeInfo.color}>{linkTypeInfo.label}</Tag>
              {link.description && <span>{link.description}</span>}
            </Space>
          }
        />
      </List.Item>
    );
  };

  return (
    <Card
      title={
        <Space>
          <LinkOutlined />
          关联知识
        </Space>
      }
      extra={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          添加关联
        </Button>
      }
    >
      <Spin spinning={loading}>
        {/* Outgoing Links */}
        {outgoingLinks.length > 0 && (
          <>
            <h4>链接到 ({outgoingLinks.length})</h4>
            <List
              size="small"
              dataSource={outgoingLinks}
              renderItem={(link) => renderLinkItem(link, 'outgoing')}
            />
          </>
        )}

        {/* Incoming Links */}
        {incomingLinks.length > 0 && (
          <>
            {outgoingLinks.length > 0 && <Divider />}
            <h4>被链接 ({incomingLinks.length})</h4>
            <List
              size="small"
              dataSource={incomingLinks}
              renderItem={(link) => renderLinkItem(link, 'incoming')}
            />
          </>
        )}

        {/* Empty State */}
        {outgoingLinks.length === 0 && incomingLinks.length === 0 && (
          <Empty
            description="暂无关联知识"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <>
            <Divider />
            <h4>💡 推荐关联</h4>
            <List
              size="small"
              dataSource={suggestions}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button
                      type="link"
                      size="small"
                      icon={<LinkOutlined />}
                      onClick={() => createLink(item.id, 'related')}
                    >
                      添加
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={item.title}
                    description={
                      <Space>
                        <span>相似度: {item.score}</span>
                        {item.reasons.map((reason, idx) => (
                          <Tag key={idx} color="blue">
                            {reason}
                          </Tag>
                        ))}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </>
        )}
      </Spin>

      {/* Add Link Modal */}
      <Modal
        title="添加关联知识"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setSelectedKnowledge(null);
          setSearchResults([]);
        }}
        onOk={() => {
          if (selectedKnowledge) {
            createLink(selectedKnowledge, selectedLinkType);
          } else {
            message.warning('请选择要关联的知识');
          }
        }}
        okText="创建关联"
        cancelText="取消"
        width={600}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* Search */}
          <Input.Search
            placeholder="搜索知识..."
            onSearch={searchKnowledge}
            loading={searchLoading}
            enterButton={<SearchOutlined />}
          />

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div>
              <h4>搜索结果</h4>
              <List
                size="small"
                dataSource={searchResults}
                renderItem={(item: any) => (
                  <List.Item
                    onClick={() => setSelectedKnowledge(item.id)}
                    style={{
                      cursor: 'pointer',
                      background:
                        selectedKnowledge === item.id ? '#e6f7ff' : 'transparent',
                      padding: '8px',
                      borderRadius: '4px',
                    }}
                  >
                    <List.Item.Meta
                      title={item.title}
                      description={
                        <Space>
                          {item.category && <Tag>{item.category}</Tag>}
                          <span>{item.word_count} 字</span>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </div>
          )}

          {/* Link Type Selection */}
          {selectedKnowledge && (
            <div>
              <h4>关联类型</h4>
              <Select
                value={selectedLinkType}
                onChange={setSelectedLinkType}
                style={{ width: '100%' }}
              >
                {Object.entries(LINK_TYPES).map(([key, value]) => (
                  <Select.Option key={key} value={key}>
                    <Tag color={value.color}>{value.label}</Tag>
                  </Select.Option>
                ))}
              </Select>
            </div>
          )}
        </Space>
      </Modal>
    </Card>
  );
};

export default RelatedKnowledgeSection;
```

### 步骤 2: 集成到知识详情页 (5分钟)

修改文件: `frontend/src/pages/knowledge/KnowledgeDetailPage.tsx`

```typescript
// 在文件顶部添加导入
import RelatedKnowledgeSection from '@/components/knowledge/RelatedKnowledgeSection';

// 在知识内容显示后添加关联知识区域
// 找到类似这样的代码：
<Card title={knowledge.title}>
  {/* 现有的知识内容 */}
  <ReactMarkdown>{knowledge.content}</ReactMarkdown>
  
  {/* 添加关联知识区域 */}
  <div style={{ marginTop: 24 }}>
    <RelatedKnowledgeSection knowledgeId={id} />
  </div>
</Card>
```

### 步骤 3: 更新API服务 (5分钟)

确保 `frontend/src/services/api.ts` 中有正确的API配置：

```typescript
// 检查是否有这些方法，如果没有则添加

// 获取知识链接
export const getKnowledgeLinks = (knowledgeId: string, direction: string = 'both') =>
  api.get(`/api/v1/knowledge/${knowledgeId}/links?direction=${direction}`);

// 创建知识链接
export const createKnowledgeLink = (knowledgeId: string, data: any) =>
  api.post(`/api/v1/knowledge/${knowledgeId}/links`, data);

// 删除知识链接
export const deleteKnowledgeLink = (linkId: string) =>
  api.delete(`/api/v1/links/${linkId}`);

// 获取相关知识推荐
export const getRelatedKnowledge = (knowledgeId: string, limit: number = 10) =>
  api.get(`/api/v1/knowledge/${knowledgeId}/related?limit=${limit}`);
```

### 步骤 4: 测试功能 (5分钟)

```bash
# 1. 确保后端和前端都在运行
cd backend && uvicorn app.main:app --reload
cd frontend && npm start

# 2. 访问任意知识详情页
http://localhost:3000/knowledge/{id}

# 3. 测试以下功能：
✅ 查看现有关联（如果有）
✅ 点击"添加关联"按钮
✅ 搜索其他知识
✅ 选择知识并选择关联类型
✅ 创建关联
✅ 查看推荐的相关知识
✅ 删除关联
```

## 🎨 样式优化（可选）

如果想要更好的视觉效果，可以添加自定义样式：

```css
/* 在组件中添加 style 对象或使用 CSS 模块 */

.related-knowledge-section {
  margin-top: 24px;
}

.link-item {
  transition: background-color 0.3s;
}

.link-item:hover {
  background-color: #f5f5f5;
}

.suggestion-item {
  border-left: 3px solid #1890ff;
  padding-left: 12px;
}
```

## 📊 验证清单

完成后，确认以下功能都正常工作：

- [ ] 可以查看outgoing链接（链接到）
- [ ] 可以查看incoming链接（被链接）
- [ ] 可以搜索并添加新的关联
- [ ] 可以选择不同的链接类型
- [ ] 可以删除现有关联
- [ ] 可以看到智能推荐的相关知识
- [ ] 可以快速添加推荐的关联
- [ ] 链接类型用不同颜色的标签显示
- [ ] 点击关联知识可以跳转到详情页

## 🐛 常见问题

### 问题 1: API 404 错误

**原因**: 后端路由未正确配置

**解决**:
```bash
# 检查后端路由
grep -r "knowledge_graph" backend/app/api/v1/api.py

# 确保包含
api_router.include_router(knowledge_graph.router, prefix="", tags=["knowledge-graph"])
```

### 问题 2: 推荐功能不工作

**原因**: 数据库中没有足够的知识或关联

**解决**:
```bash
# 创建更多测试数据
# 至少创建5-10个知识条目
# 设置相同的分类或标签
```

### 问题 3: 搜索无结果

**原因**: 搜索API路径或参数错误

**解决**:
```typescript
// 检查搜索API调用
const res = await api.get(`/api/v1/search?q=${encodeURIComponent(keyword)}`);

// 确保后端搜索端点正常工作
curl "http://localhost:8000/api/v1/search?q=test"
```

## 🚀 下一步

完成基础功能后，可以继续实现：

1. **链接描述**: 为每个链接添加描述文字
2. **批量操作**: 一次添加多个关联
3. **可视化预览**: 在详情页显示小型图谱
4. **快捷键**: 使用快捷键快速添加关联
5. **拖拽排序**: 调整关联知识的显示顺序

## 📚 相关文档

- [知识图谱完整路线图](KNOWLEDGE_GRAPH_ROADMAP.md)
- [API文档](http://localhost:8000/docs)
- [Ant Design 组件库](https://ant.design/components/overview-cn/)

---

**🎉 恭喜！您已经成功实现了知识详情页的关联功能！**

这是知识图谱最重要的功能，将大大提升用户体验。

---

*最后更新: 2026-02-10*
*预计完成时间: 30分钟*
