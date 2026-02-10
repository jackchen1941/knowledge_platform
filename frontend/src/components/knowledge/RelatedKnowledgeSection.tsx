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
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  LinkOutlined,
  ArrowRightOutlined,
  ArrowLeftOutlined,
  SearchOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import api from '@/services/api';
import { formatErrorMessage } from '@/utils/errorHandler';

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
  example: { label: '示例', color: 'magenta' },
  opposite: { label: '对比', color: 'red' },
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
  const [linkDescription, setLinkDescription] = useState('');

  useEffect(() => {
    loadLinks();
    loadSuggestions();
  }, [knowledgeId]);

  const loadLinks = async () => {
    setLoading(true);
    try {
      // 获取outgoing链接
      const outgoingRes = await api.get(
        `/knowledge/${knowledgeId}/links?direction=outgoing`
      );
      setOutgoingLinks(outgoingRes.data || []);

      // 获取incoming链接
      const incomingRes = await api.get(
        `/knowledge/${knowledgeId}/links?direction=incoming`
      );
      setIncomingLinks(incomingRes.data || []);
    } catch (error) {
      console.error('加载关联知识失败', error);
      message.error('加载关联知识失败');
    } finally {
      setLoading(false);
    }
  };

  const loadSuggestions = async () => {
    try {
      const res = await api.get(`/knowledge/${knowledgeId}/related?limit=5`);
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
      const res = await api.get(`/search?q=${encodeURIComponent(keyword)}`);
      // 过滤掉当前知识和已关联的知识
      const existingIds = new Set([
        knowledgeId,
        ...outgoingLinks.map(l => l.target_id),
        ...incomingLinks.map(l => l.source_id),
      ]);
      const filtered = (res.data.items || []).filter(
        (item: any) => !existingIds.has(item.id)
      );
      setSearchResults(filtered);
    } catch (error) {
      console.error('搜索失败', error);
      message.error('搜索失败');
    } finally {
      setSearchLoading(false);
    }
  };

  const createLink = async (targetId: string, linkType: string, description?: string) => {
    try {
      await api.post(`/knowledge/${knowledgeId}/links`, {
        target_id: targetId,
        link_type: linkType,
        description: description || null,
      });
      message.success('关联创建成功');
      loadLinks();
      loadSuggestions();
      setModalVisible(false);
      setSelectedKnowledge(null);
      setLinkDescription('');
    } catch (error: any) {
      console.error('创建关联失败', error);
      message.error(formatErrorMessage(error, '创建关联失败'));
    }
  };

  const deleteLink = async (linkId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个关联吗？',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await api.delete(`/links/${linkId}`);
          message.success('关联已删除');
          loadLinks();
          loadSuggestions();
        } catch (error) {
          console.error('删除失败', error);
          message.error('删除失败');
        }
      },
    });
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
              <Tooltip title="链接到">
                <ArrowRightOutlined style={{ fontSize: 16, color: '#1890ff' }} />
              </Tooltip>
            ) : (
              <Tooltip title="被链接">
                <ArrowLeftOutlined style={{ fontSize: 16, color: '#52c41a' }} />
              </Tooltip>
            )
          }
          title={
            <a href={`/knowledge/${targetId}`} target="_blank" rel="noopener noreferrer">
              {title || '未知标题'}
            </a>
          }
          description={
            <Space>
              <Tag color={linkTypeInfo.color}>{linkTypeInfo.label}</Tag>
              {link.description && <span style={{ color: '#666' }}>{link.description}</span>}
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
      style={{ marginTop: 24 }}
    >
      <Spin spinning={loading}>
        {/* Outgoing Links */}
        {outgoingLinks.length > 0 && (
          <>
            <h4 style={{ marginBottom: 12 }}>
              <ArrowRightOutlined style={{ marginRight: 8, color: '#1890ff' }} />
              链接到 ({outgoingLinks.length})
            </h4>
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
            <h4 style={{ marginBottom: 12 }}>
              <ArrowLeftOutlined style={{ marginRight: 8, color: '#52c41a' }} />
              被链接 ({incomingLinks.length})
            </h4>
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
            style={{ padding: '20px 0' }}
          >
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
              添加第一个关联
            </Button>
          </Empty>
        )}

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <>
            <Divider />
            <h4 style={{ marginBottom: 12 }}>
              <BulbOutlined style={{ marginRight: 8, color: '#faad14' }} />
              推荐关联
            </h4>
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
                      <Space wrap>
                        <span style={{ color: '#666' }}>相似度: {item.score}</span>
                        {item.reasons.map((reason, idx) => (
                          <Tag key={idx} color="blue" style={{ margin: 0 }}>
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
          setLinkDescription('');
        }}
        onOk={() => {
          if (selectedKnowledge) {
            createLink(selectedKnowledge, selectedLinkType, linkDescription);
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
          <div>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
              搜索知识
            </label>
            <Input.Search
              placeholder="输入关键词搜索..."
              onSearch={searchKnowledge}
              loading={searchLoading}
              enterButton={<SearchOutlined />}
              allowClear
            />
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div>
              <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                搜索结果 ({searchResults.length})
              </label>
              <div style={{ maxHeight: 300, overflowY: 'auto', border: '1px solid #d9d9d9', borderRadius: 4 }}>
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
                        padding: '12px 16px',
                        transition: 'background 0.3s',
                      }}
                      onMouseEnter={(e) => {
                        if (selectedKnowledge !== item.id) {
                          e.currentTarget.style.background = '#f5f5f5';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (selectedKnowledge !== item.id) {
                          e.currentTarget.style.background = 'transparent';
                        }
                      }}
                    >
                      <List.Item.Meta
                        title={
                          <span style={{ fontWeight: selectedKnowledge === item.id ? 600 : 400 }}>
                            {item.title}
                          </span>
                        }
                        description={
                          <Space size="small">
                            {item.category && <Tag>{item.category}</Tag>}
                            <span style={{ color: '#999' }}>{item.word_count} 字</span>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
            </div>
          )}

          {/* Link Type Selection */}
          {selectedKnowledge && (
            <>
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                  关联类型 *
                </label>
                <Select
                  value={selectedLinkType}
                  onChange={setSelectedLinkType}
                  style={{ width: '100%' }}
                  size="large"
                >
                  {Object.entries(LINK_TYPES).map(([key, value]) => (
                    <Select.Option key={key} value={key}>
                      <Tag color={value.color} style={{ marginRight: 8 }}>
                        {value.label}
                      </Tag>
                    </Select.Option>
                  ))}
                </Select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                  描述（可选）
                </label>
                <Input.TextArea
                  value={linkDescription}
                  onChange={(e) => setLinkDescription(e.target.value)}
                  placeholder="添加关于这个关联的说明..."
                  rows={3}
                  maxLength={200}
                  showCount
                />
              </div>
            </>
          )}
        </Space>
      </Modal>
    </Card>
  );
};

export default RelatedKnowledgeSection;
