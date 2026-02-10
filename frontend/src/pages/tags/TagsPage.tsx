import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TagsOutlined,
  MergeCellsOutlined,
} from '@ant-design/icons';
import { tagsAPI } from '@/services/api';

const { Title } = Typography;

interface Tag {
  id: string;
  name: string;
  description: string;
  color: string;
  usage_count: number;
  is_system: boolean;
}

const TagsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Tag[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [mergeModalVisible, setMergeModalVisible] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [form] = Form.useForm();
  const [mergeForm] = Form.useForm();
  const [popularTags, setPopularTags] = useState<Tag[]>([]);

  useEffect(() => {
    fetchData();
    fetchPopularTags();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await tagsAPI.list();
      setData(response.data.tags || []);
    } catch (error: any) {
      console.warn('Tags API not available, using empty list');
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPopularTags = async () => {
    try {
      const response = await tagsAPI.getPopular(10);
      setPopularTags(response.data.tags || []);
    } catch (error) {
      console.warn('Popular tags API not available, using empty list');
      setPopularTags([]);
    }
  };

  const handleCreate = () => {
    setEditingTag(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (tag: Tag) => {
    setEditingTag(tag);
    form.setFieldsValue(tag);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await tagsAPI.delete(id);
      message.success('删除成功');
      fetchData();
      fetchPopularTags();
    } catch (error: any) {
      console.error('Failed to delete tag:', error);
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingTag) {
        await tagsAPI.update(editingTag.id, values);
        message.success('更新成功');
      } else {
        await tagsAPI.create(values);
        message.success('创建成功');
      }
      
      setModalVisible(false);
      fetchData();
      fetchPopularTags();
    } catch (error: any) {
      console.error('Failed to save tag:', error);
      message.error(error.response?.data?.detail || '保存失败');
    }
  };

  const handleMerge = async () => {
    try {
      const values = await mergeForm.validateFields();
      await tagsAPI.merge(values.source_tag_id, values.target_tag_id);
      message.success('合并成功');
      setMergeModalVisible(false);
      mergeForm.resetFields();
      fetchData();
      fetchPopularTags();
    } catch (error: any) {
      console.error('Failed to merge tags:', error);
      message.error(error.response?.data?.detail || '合并失败');
    }
  };

  const columns = [
    {
      title: '标签',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Tag) => (
        <Tag color={record.color} style={{ fontSize: '14px', padding: '4px 12px' }}>
          {text}
        </Tag>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '颜色',
      dataIndex: 'color',
      key: 'color',
      width: 100,
      render: (color: string) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div
            style={{
              width: 20,
              height: 20,
              backgroundColor: color,
              borderRadius: 4,
              marginRight: 8,
            }}
          />
          <span>{color}</span>
        </div>
      ),
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count',
      width: 100,
      align: 'right' as const,
      sorter: (a: Tag, b: Tag) => a.usage_count - b.usage_count,
    },
    {
      title: '类型',
      dataIndex: 'is_system',
      key: 'is_system',
      width: 100,
      render: (isSystem: boolean) => (
        <Tag color={isSystem ? 'purple' : 'default'}>
          {isSystem ? '系统' : '自定义'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: Tag) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={record.is_system}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
            disabled={record.is_system}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={record.is_system}
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
        <Title level={2} style={{ margin: 0 }}>标签管理</Title>
        <Space>
          <Button
            icon={<MergeCellsOutlined />}
            onClick={() => setMergeModalVisible(true)}
          >
            合并标签
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            新建标签
          </Button>
        </Space>
      </div>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总标签数"
              value={data.length}
              prefix={<TagsOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="自定义标签"
              value={data.filter(t => !t.is_system).length}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总使用次数"
              value={data.reduce((sum, t) => sum + t.usage_count, 0)}
            />
          </Card>
        </Col>
      </Row>

      {/* Popular Tags */}
      {popularTags.length > 0 && (
        <Card title="热门标签" style={{ marginBottom: 16 }}>
          <Space size="middle" wrap>
            {popularTags.map((tag) => (
              <Tag
                key={tag.id}
                color={tag.color}
                style={{ fontSize: '16px', padding: '6px 16px' }}
              >
                {tag.name} ({tag.usage_count})
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      {/* Tags Table */}
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      {/* Create/Edit Modal */}
      <Modal
        title={editingTag ? '编辑标签' : '新建标签'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="标签名称"
            rules={[{ required: true, message: '请输入标签名称' }]}
          >
            <Input placeholder="输入标签名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea
              placeholder="输入标签描述（可选）"
              rows={3}
            />
          </Form.Item>

          <Form.Item
            name="color"
            label="颜色"
            rules={[
              { required: true, message: '请输入颜色' },
              { pattern: /^#[0-9A-Fa-f]{6}$/, message: '请输入有效的十六进制颜色（如 #1890ff）' },
            ]}
          >
            <Input
              placeholder="#1890ff"
              addonBefore={
                <div
                  style={{
                    width: 20,
                    height: 20,
                    backgroundColor: form.getFieldValue('color') || '#1890ff',
                    borderRadius: 4,
                  }}
                />
              }
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Merge Modal */}
      <Modal
        title="合并标签"
        open={mergeModalVisible}
        onOk={handleMerge}
        onCancel={() => setMergeModalVisible(false)}
        okText="合并"
        cancelText="取消"
      >
        <Form form={mergeForm} layout="vertical">
          <Form.Item
            name="source_tag_id"
            label="源标签（将被删除）"
            rules={[{ required: true, message: '请选择源标签' }]}
          >
            <Select
              placeholder="选择要合并的标签"
              showSearch
              filterOption={(input: string, option: any) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={data.filter(t => !t.is_system).map((tag) => ({
                label: tag.name,
                value: tag.id,
              }))}
            />
          </Form.Item>

          <Form.Item
            name="target_tag_id"
            label="目标标签（将保留）"
            rules={[{ required: true, message: '请选择目标标签' }]}
          >
            <Select
              placeholder="选择目标标签"
              showSearch
              filterOption={(input: string, option: any) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={data.filter(t => !t.is_system).map((tag) => ({
                label: tag.name,
                value: tag.id,
              }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TagsPage;
