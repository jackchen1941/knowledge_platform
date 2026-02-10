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
  Switch,
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
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { usersAPI } from '@/services/api';

const { Title } = Typography;

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
}

const UsersManagementPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchData();
    fetchStats();
  }, [page, pageSize]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await usersAPI.list({ page, page_size: pageSize });
      setData(response.data.users || []);
      setTotal(response.data.total || 0);
    } catch (error: any) {
      console.warn('Users API not available, using empty list');
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await usersAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.warn('User stats API not available');
    }
  };

  const handleCreate = () => {
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue({
      ...user,
      password: undefined, // Don't show password
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await usersAPI.delete(id);
      message.success('删除成功');
      fetchData();
      fetchStats();
    } catch (error: any) {
      console.error('Failed to delete user:', error);
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingUser) {
        await usersAPI.update(editingUser.id, values);
        message.success('更新成功');
      } else {
        await usersAPI.create(values);
        message.success('创建成功');
      }
      
      setModalVisible(false);
      fetchData();
      fetchStats();
    } catch (error: any) {
      console.error('Failed to save user:', error);
      message.error(error.response?.data?.detail || '保存失败');
    }
  };

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: '15%',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: '20%',
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
      width: '15%',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: '10%',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'} icon={isActive ? <CheckCircleOutlined /> : <CloseCircleOutlined />}>
          {isActive ? '活跃' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '验证',
      dataIndex: 'is_verified',
      key: 'is_verified',
      width: '10%',
      render: (isVerified: boolean) => (
        <Tag color={isVerified ? 'blue' : 'default'}>
          {isVerified ? '已验证' : '未验证'}
        </Tag>
      ),
    },
    {
      title: '角色',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      width: '10%',
      render: (isSuperuser: boolean) => (
        <Tag color={isSuperuser ? 'purple' : 'default'}>
          {isSuperuser ? '管理员' : '普通用户'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: '12%',
      render: (date: string) => new Date(date).toLocaleDateString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: '12%',
      render: (_: any, record: User) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除吗？"
            description="删除用户将无法恢复"
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
        <Title level={2} style={{ margin: 0 }}>用户管理</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreate}
        >
          新建用户
        </Button>
      </div>

      {/* Statistics */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={8} lg={6}>
            <Card>
              <Statistic
                title="总用户数"
                value={stats.total_users}
                prefix={<TeamOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8} lg={6}>
            <Card>
              <Statistic
                title="活跃用户"
                value={stats.active_users}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8} lg={6}>
            <Card>
              <Statistic
                title="已验证用户"
                value={stats.verified_users}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8} lg={6}>
            <Card>
              <Statistic
                title="管理员"
                value={stats.superusers}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Users Table */}
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

      {/* Create/Edit Modal */}
      <Modal
        title={editingUser ? '编辑用户' : '新建用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="保存"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="输入用户名" />
          </Form.Item>

          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="输入邮箱" />
          </Form.Item>

          <Form.Item
            name="full_name"
            label="姓名"
          >
            <Input placeholder="输入姓名（可选）" />
          </Form.Item>

          <Form.Item
            name="password"
            label={editingUser ? "密码（留空则不修改）" : "密码"}
            rules={editingUser ? [] : [{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="输入密码" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="is_active"
                label="活跃状态"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="活跃" unCheckedChildren="禁用" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="is_verified"
                label="验证状态"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch checkedChildren="已验证" unCheckedChildren="未验证" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="is_superuser"
                label="管理员"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default UsersManagementPage;
