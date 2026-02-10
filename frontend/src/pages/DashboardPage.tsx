import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Spin, List, Tag } from 'antd';
import {
  FileTextOutlined,
  FolderOutlined,
  TagsOutlined,
  EyeOutlined,
  EditOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { analyticsAPI, knowledgeAPI } from '@/services/api';

const { Title, Text } = Typography;

interface OverviewStats {
  total_items: number;
  published_items: number;
  draft_items: number;
  total_words: number;
  total_views: number;
  total_tags: number;
  total_categories: number;
}

interface RecentItem {
  id: string;
  title: string;
  updated_at: string;
  is_published: boolean;
}

const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [recentItems, setRecentItems] = useState<RecentItem[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch overview stats
      try {
        const statsResponse = await analyticsAPI.overview();
        setStats(statsResponse.data);
      } catch (error) {
        console.warn('Analytics API not available, using default stats');
        // 设置默认值，不显示错误
        setStats({
          total_items: 0,
          published_items: 0,
          draft_items: 0,
          total_words: 0,
          total_views: 0,
          total_tags: 0,
          total_categories: 0,
        });
      }

      // Fetch recent items
      try {
        const itemsResponse = await knowledgeAPI.list({
          page: 1,
          page_size: 5,
          sort_by: 'updated_at',
          sort_order: 'desc',
        });
        setRecentItems(itemsResponse.data.items || []);
      } catch (error) {
        console.warn('Knowledge API not available, showing empty list');
        setRecentItems([]);
      }
    } catch (error: any) {
      console.error('Failed to fetch dashboard data:', error);
      // 不显示错误消息，使用默认空数据
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        仪表盘
      </Title>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总知识条目"
              value={stats?.total_items || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已发布"
              value={stats?.published_items || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="草稿"
              value={stats?.draft_items || 0}
              prefix={<EditOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总浏览量"
              value={stats?.total_views || 0}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总字数"
              value={stats?.total_words || 0}
              suffix="字"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="分类数"
              value={stats?.total_categories || 0}
              prefix={<FolderOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="标签数"
              value={stats?.total_tags || 0}
              prefix={<TagsOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均字数"
              value={Math.round((stats?.total_words || 0) / (stats?.total_items || 1))}
              suffix="字/篇"
            />
          </Card>
        </Col>
      </Row>

      {/* Recent Items */}
      <Card title="最近更新" style={{ marginBottom: 24 }}>
        <List
          dataSource={recentItems}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <a href={`/knowledge/${item.id}`}>
                    {item.title}
                  </a>
                }
                description={
                  <span>
                    更新于 {new Date(item.updated_at).toLocaleString('zh-CN')}
                    {' '}
                    {item.is_published ? (
                      <Tag color="success">已发布</Tag>
                    ) : (
                      <Tag color="warning">草稿</Tag>
                    )}
                  </span>
                }
              />
            </List.Item>
          )}
          locale={{ emptyText: '暂无数据' }}
        />
      </Card>

      {/* Quick Actions */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={8}>
          <Card
            hoverable
            onClick={() => window.location.href = '/knowledge/new'}
            style={{ textAlign: 'center', cursor: 'pointer' }}
          >
            <FileTextOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
            <Title level={4}>创建知识条目</Title>
            <Text type="secondary">开始记录新的知识</Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card
            hoverable
            onClick={() => window.location.href = '/search'}
            style={{ textAlign: 'center', cursor: 'pointer' }}
          >
            <EyeOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
            <Title level={4}>搜索知识</Title>
            <Text type="secondary">查找已有的知识内容</Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card
            hoverable
            onClick={() => window.location.href = '/analytics'}
            style={{ textAlign: 'center', cursor: 'pointer' }}
          >
            <TagsOutlined style={{ fontSize: 48, color: '#722ed1', marginBottom: 16 }} />
            <Title level={4}>查看统计</Title>
            <Text type="secondary">分析知识管理情况</Text>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
