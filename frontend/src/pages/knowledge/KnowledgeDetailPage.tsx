import React, { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Tag,
  Space,
  Button,
  Divider,
  Spin,
  message,
  Descriptions,
  List,
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  FolderOutlined,
  TagsOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { knowledgeAPI } from '@/services/api';
import ReactMarkdown from 'react-markdown';

const { Title, Text, Paragraph } = Typography;

interface KnowledgeDetail {
  id: string;
  title: string;
  content: string;
  content_type: string;
  summary: string;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  published_at: string;
  word_count: number;
  reading_time: number;
  view_count: number;
  category: { id: string; name: string; full_path: string } | null;
  tags: Array<{ id: string; name: string; color: string }>;
  attachments: Array<{ id: string; filename: string; file_size_human: string }>;
}

const KnowledgeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<KnowledgeDetail | null>(null);

  useEffect(() => {
    if (id) {
      fetchData();
    }
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await knowledgeAPI.get(id!);
      setData(response.data);
    } catch (error: any) {
      console.error('Failed to fetch knowledge item:', error);
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await knowledgeAPI.delete(id!);
      message.success('删除成功');
      navigate('/knowledge');
    } catch (error: any) {
      console.error('Failed to delete:', error);
      message.error('删除失败');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!data) {
    return <div>未找到内容</div>;
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/knowledge')}
          style={{ marginBottom: 16 }}
        >
          返回列表
        </Button>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              {data.title}
            </Title>
            <Space size="middle" wrap>
              <Tag color={data.is_published ? 'success' : 'warning'}>
                {data.is_published ? '已发布' : '草稿'}
              </Tag>
              {data.category && (
                <Tag icon={<FolderOutlined />} color="blue">
                  {data.category.full_path}
                </Tag>
              )}
              <Text type="secondary">
                <EyeOutlined /> {data.view_count} 次浏览
              </Text>
              <Text type="secondary">
                <FileTextOutlined /> {data.word_count} 字
              </Text>
              <Text type="secondary">
                <ClockCircleOutlined /> 约 {data.reading_time} 分钟阅读
              </Text>
            </Space>
          </div>

          <Space>
            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={() => navigate(`/knowledge/${id}/edit`)}
            >
              编辑
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleDelete}
            >
              删除
            </Button>
          </Space>
        </div>
      </div>

      {/* Summary */}
      {data.summary && (
        <Card style={{ marginBottom: 16, background: '#f0f5ff' }}>
          <Paragraph style={{ margin: 0, fontSize: '16px' }}>
            <strong>摘要：</strong>{data.summary}
          </Paragraph>
        </Card>
      )}

      {/* Tags */}
      {data.tags.length > 0 && (
        <Card style={{ marginBottom: 16 }}>
          <Space size="small" wrap>
            <TagsOutlined />
            {data.tags.map((tag) => (
              <Tag key={tag.id} color={tag.color}>
                {tag.name}
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      {/* Content */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ fontSize: '16px', lineHeight: '1.8' }}>
          {data.content_type === 'markdown' ? (
            <ReactMarkdown>{data.content}</ReactMarkdown>
          ) : (
            <div dangerouslySetInnerHTML={{ __html: data.content }} />
          )}
        </div>
      </Card>

      {/* Attachments */}
      {data.attachments.length > 0 && (
        <Card title="附件" style={{ marginBottom: 16 }}>
          <List
            dataSource={data.attachments}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={item.filename}
                  description={`大小: ${item.file_size_human}`}
                />
                <Button type="link">下载</Button>
              </List.Item>
            )}
          />
        </Card>
      )}

      {/* Metadata */}
      <Card title="元数据">
        <Descriptions column={2}>
          <Descriptions.Item label="创建时间">
            {new Date(data.created_at).toLocaleString('zh-CN')}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {new Date(data.updated_at).toLocaleString('zh-CN')}
          </Descriptions.Item>
          {data.published_at && (
            <Descriptions.Item label="发布时间">
              {new Date(data.published_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
          )}
          <Descriptions.Item label="内容类型">
            {data.content_type}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default KnowledgeDetailPage;
