import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  Typography,
  message,
  Popconfirm,
  Card,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { knowledgeAPI, categoriesAPI, tagsAPI } from '@/services/api';

const { Title } = Typography;
const { Search } = Input;

interface KnowledgeItem {
  id: string;
  title: string;
  summary: string;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  word_count: number;
  view_count: number;
  category: { id: string; name: string } | null;
  tags: Array<{ id: string; name: string; color: string }>;
}

const KnowledgeListPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<KnowledgeItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchText, setSearchText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<boolean | undefined>();
  const [categories, setCategories] = useState<any[]>([]);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchData();
  }, [page, pageSize, searchText, selectedCategory, selectedStatus]);

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.list();
      setCategories(response.data.categories || []);
    } catch (error) {
      console.warn('Categories API not available, using empty list');
      setCategories([]);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const params: any = {
        page,
        page_size: pageSize,
        sort_by: 'updated_at',
        sort_order: 'desc',
      };

      if (searchText) {
        params.search = searchText;
      }
      if (selectedCategory) {
        params.category_id = selectedCategory;
      }
      if (selectedStatus !== undefined) {
        params.is_published = selectedStatus;
      }

      const response = await knowledgeAPI.list(params);
      setData(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch (error: any) {
      console.warn('Knowledge API not available, showing empty list');
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await knowledgeAPI.delete(id);
      message.success('删除成功');
      fetchData();
    } catch (error: any) {
      console.error('Failed to delete:', error);
      message.error('删除失败');
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '30%',
      render: (text: string, record: KnowledgeItem) => (
        <a onClick={() => navigate(`/knowledge/${record.id}`)}>
          {text}
        </a>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: '12%',
      render: (category: any) => (
        category ? <Tag color="blue">{category.name}</Tag> : <Tag>未分类</Tag>
      ),
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: '15%',
      render: (tags: any[]) => (
        <>
          {tags.slice(0, 3).map((tag) => (
            <Tag key={tag.id} color={tag.color}>
              {tag.name}
            </Tag>
          ))}
          {tags.length > 3 && <Tag>+{tags.length - 3}</Tag>}
        </>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_published',
      key: 'is_published',
      width: '8%',
      render: (isPublished: boolean) => (
        <Tag color={isPublished ? 'success' : 'warning'}>
          {isPublished ? '已发布' : '草稿'}
        </Tag>
      ),
    },
    {
      title: '字数',
      dataIndex: 'word_count',
      key: 'word_count',
      width: '8%',
      render: (count: number) => `${count}字`,
    },
    {
      title: '浏览',
      dataIndex: 'view_count',
      key: 'view_count',
      width: '8%',
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: '12%',
      render: (date: string) => new Date(date).toLocaleDateString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: '12%',
      render: (_: any, record: KnowledgeItem) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/knowledge/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/knowledge/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ margin: 0 }}>知识库</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/knowledge/new')}
        >
          新建知识
        </Button>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space size="middle" wrap>
          <Search
            placeholder="搜索标题或内容"
            allowClear
            style={{ width: 300 }}
            onSearch={setSearchText}
            enterButton={<SearchOutlined />}
          />
          <Select
            placeholder="选择分类"
            allowClear
            style={{ width: 200 }}
            onChange={setSelectedCategory}
            options={[
              { label: '全部分类', value: undefined },
              ...categories.map((cat) => ({
                label: cat.name,
                value: cat.id,
              })),
            ]}
          />
          <Select
            placeholder="选择状态"
            allowClear
            style={{ width: 150 }}
            onChange={setSelectedStatus}
            options={[
              { label: '全部状态', value: undefined },
              { label: '已发布', value: true },
              { label: '草稿', value: false },
            ]}
          />
        </Space>
      </Card>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page);
            setPageSize(pageSize);
          },
        }}
      />
    </div>
  );
};

export default KnowledgeListPage;
