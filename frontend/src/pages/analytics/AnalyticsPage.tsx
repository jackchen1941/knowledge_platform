import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Spin, Table, Tag } from 'antd';
import {
  FileTextOutlined,
  FolderOutlined,
  TagsOutlined,
  EyeOutlined,
  LineChartOutlined,
  PieChartOutlined,
} from '@ant-design/icons';
import { analyticsAPI } from '@/services/api';

const { Title } = Typography;

interface OverviewStats {
  total_items: number;
  published_items: number;
  draft_items: number;
  total_words: number;
  total_views: number;
  total_tags: number;
  total_categories: number;
  average_words_per_item: number;
}

interface TopTag {
  name: string;
  color: string;
  usage_count: number;
}

interface DistributionItem {
  name?: string;
  type?: string;
  count: number;
}

const AnalyticsPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [topTags, setTopTags] = useState<TopTag[]>([]);
  const [categoryDist, setCategoryDist] = useState<DistributionItem[]>([]);
  const [wordCountDist, setWordCountDist] = useState<any[]>([]);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);

      // Fetch overview stats
      try {
        const overviewRes = await analyticsAPI.overview();
        setStats(overviewRes.data);
      } catch (error) {
        console.warn('Overview API not available, using default stats');
        setStats({
          total_items: 0,
          published_items: 0,
          draft_items: 0,
          total_words: 0,
          total_views: 0,
          total_tags: 0,
          total_categories: 0,
          average_words_per_item: 0,
        });
      }

      // Fetch top tags
      try {
        const tagsRes = await analyticsAPI.topTags(10);
        setTopTags(tagsRes.data.tags || []);
      } catch (error) {
        console.warn('Top tags API not available, using empty list');
        setTopTags([]);
      }

      // Fetch distribution
      try {
        const distRes = await analyticsAPI.distribution();
        setCategoryDist(distRes.data.by_category || []);
      } catch (error) {
        console.warn('Distribution API not available, using empty list');
        setCategoryDist([]);
      }

      // Fetch word count distribution
      try {
        const wordCountRes = await analyticsAPI.wordCount();
        setWordCountDist(wordCountRes.data.distribution || []);
      } catch (error) {
        console.warn('Word count API not available, using empty list');
        setWordCountDist([]);
      }
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

  const tagColumns = [
    {
      title: '标签',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: TopTag) => (
        <Tag color={record.color}>{text}</Tag>
      ),
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count',
      align: 'right' as const,
    },
  ];

  const categoryColumns = [
    {
      title: '分类',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
      align: 'right' as const,
    },
  ];

  const wordCountColumns = [
    {
      title: '字数范围',
      dataIndex: 'range',
      key: 'range',
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
      align: 'right' as const,
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        统计分析
      </Title>

      {/* Overview Statistics */}
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
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="草稿"
              value={stats?.draft_items || 0}
              prefix={<FileTextOutlined />}
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
              title="平均字数"
              value={stats?.average_words_per_item || 0}
              suffix="字/篇"
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
      </Row>

      {/* Charts and Tables */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                <TagsOutlined /> 热门标签 Top 10
              </span>
            }
          >
            <Table
              dataSource={topTags}
              columns={tagColumns}
              pagination={false}
              size="small"
              rowKey="name"
            />
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                <PieChartOutlined /> 分类分布
              </span>
            }
          >
            <Table
              dataSource={categoryDist}
              columns={categoryColumns}
              pagination={false}
              size="small"
              rowKey="name"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card
            title={
              <span>
                <LineChartOutlined /> 字数分布
              </span>
            }
          >
            <Table
              dataSource={wordCountDist}
              columns={wordCountColumns}
              pagination={false}
              size="small"
              rowKey="range"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AnalyticsPage;
