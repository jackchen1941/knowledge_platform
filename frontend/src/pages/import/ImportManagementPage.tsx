import React, { useEffect, useState } from 'react';
import {
  Card,
  Button,
  Table,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Space,
  Tag,
  Descriptions,
  Tabs,
  Progress,
  Alert,
  List,
  Typography,
  Divider,
} from 'antd';
import {
  PlusOutlined,
  ImportOutlined,
  DeleteOutlined,
  EditOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LinkOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import api from '../../services/api';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

interface Platform {
  platform: string;
  name: string;
  description: string;
  required_config: string[];
  optional_config: string[];
  example_config: any;
}

interface ImportConfig {
  id: string;
  name: string;
  platform: string;
  config: any;
  auto_sync: boolean;
  sync_interval: number;
  is_active: boolean;
  last_sync: string | null;
  created_at: string;
}

interface ImportTask {
  id: string;
  config_id: string;
  status: string;
  items_total: number;
  items_imported: number;
  items_failed: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

const ImportManagementPage: React.FC = () => {
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [configs, setConfigs] = useState<ImportConfig[]>([]);
  const [tasks, setTasks] = useState<ImportTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingConfig, setEditingConfig] = useState<ImportConfig | null>(null);
  const [form] = Form.useForm();
  const [urlForm] = Form.useForm();
  const [batchUrlForm] = Form.useForm();
  const [urlImporting, setUrlImporting] = useState(false);
  const [batchUrlImporting, setBatchUrlImporting] = useState(false);

  useEffect(() => {
    loadPlatforms();
    loadConfigs();
    loadTasks();
  }, []);

  const loadPlatforms = async () => {
    try {
      const response = await api.get('/import-adapters/platforms');
      setPlatforms(response.data);
    } catch (error) {
      message.error('加载平台列表失败');
    }
  };

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const response = await api.get('/import-adapters/configs');
      setConfigs(response.data);
    } catch (error) {
      message.error('加载配置列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    try {
      const response = await api.get('/import-adapters/tasks');
      setTasks(response.data);
    } catch (error) {
      message.error('加载任务列表失败');
    }
  };

  const handleCreate = () => {
    setEditingConfig(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (config: ImportConfig) => {
    setEditingConfig(config);
    form.setFieldsValue({
      name: config.name,
      platform: config.platform,
      config: JSON.stringify(config.config, null, 2),
      auto_sync: config.auto_sync,
      sync_interval: config.sync_interval,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个导入配置吗？',
      onOk: async () => {
        try {
          await api.delete(`/import-adapters/configs/${id}`);
          message.success('删除成功');
          loadConfigs();
        } catch (error) {
          message.error('删除失败');
        }
      },
    });
  };

  const handleSubmit = async (values: any) => {
    try {
      const configData = {
        name: values.name,
        platform: values.platform,
        config: JSON.parse(values.config),
        auto_sync: values.auto_sync || false,
        sync_interval: values.sync_interval || 3600,
      };

      if (editingConfig) {
        await api.put(`/import-adapters/configs/${editingConfig.id}`, configData);
        message.success('更新成功');
      } else {
        await api.post('/import-adapters/configs', configData);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadConfigs();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const handleImport = async (configId: string) => {
    try {
      const response = await api.post(`/import-adapters/configs/${configId}/import`, {
        config_id: configId,
      });
      
      message.success(`导入成功！导入了 ${response.data.items_imported} 条，失败 ${response.data.items_failed} 条`);
      loadTasks();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '导入失败');
    }
  };

  const getPlatformName = (platform: string) => {
    const p = platforms.find(p => p.platform === platform);
    return p ? p.name : platform;
  };

  const handleUrlImport = async (values: any) => {
    setUrlImporting(true);
    try {
      const params = new URLSearchParams({
        url: values.url,
      });
      
      if (values.category) {
        params.append('category', values.category);
      }
      
      if (values.tags) {
        const tags = values.tags.split(',').map((t: string) => t.trim()).filter((t: string) => t);
        tags.forEach((tag: string) => params.append('tags', tag));
      }

      const response = await api.post(`/import-adapters/import-url?${params.toString()}`);
      
      message.success(`导入成功！标题：${response.data.title}`);
      urlForm.resetFields();
    } catch (error: any) {
      console.error('Import error:', error);
      const errorMsg = error.response?.data?.detail || error.message || '导入失败';
      message.error(errorMsg, 5); // 显示5秒
      
      // 如果是网络错误，给出更详细的提示
      if (error.message?.includes('Network Error') || error.code === 'ECONNABORTED') {
        message.warning('网络连接问题，请检查URL是否可访问或稍后重试', 5);
      }
    } finally {
      setUrlImporting(false);
    }
  };

  const handleBatchUrlImport = async (values: any) => {
    setBatchUrlImporting(true);
    try {
      const urls = values.urls.split('\n').map((u: string) => u.trim()).filter((u: string) => u);
      
      if (urls.length === 0) {
        message.warning('请输入至少一个URL');
        setBatchUrlImporting(false);
        return;
      }

      const tags = values.batch_tags 
        ? values.batch_tags.split(',').map((t: string) => t.trim()).filter((t: string) => t)
        : [];

      const response = await api.post('/import-adapters/import-urls', {
        urls,
        category: values.batch_category || undefined,
        tags: tags.length > 0 ? tags : undefined,
      });
      
      message.success(
        `批量导入完成！成功：${response.data.successful}，失败：${response.data.failed}`
      );
      
      // 显示详细结果
      Modal.info({
        title: '批量导入结果',
        width: 600,
        content: (
          <List
            size="small"
            dataSource={response.data.results}
            renderItem={(item: any) => (
              <List.Item>
                {item.success ? (
                  <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                ) : (
                  <CloseCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
                )}
                <div style={{ flex: 1 }}>
                  <div>{item.url}</div>
                  {item.success ? (
                    <Text type="secondary">标题: {item.title}</Text>
                  ) : (
                    <Text type="danger">错误: {item.error}</Text>
                  )}
                </div>
              </List.Item>
            )}
          />
        ),
      });
      
      batchUrlForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量导入失败');
    } finally {
      setBatchUrlImporting(false);
    }
  };

  const configColumns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform: string) => getPlatformName(platform),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'default'}>
          {active ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '自动同步',
      dataIndex: 'auto_sync',
      key: 'auto_sync',
      render: (auto: boolean) => (auto ? '是' : '否'),
    },
    {
      title: '最后同步',
      dataIndex: 'last_sync',
      key: 'last_sync',
      render: (date: string | null) => date ? new Date(date).toLocaleString() : '从未',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: ImportConfig) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<ImportOutlined />}
            onClick={() => handleImport(record.id)}
          >
            导入
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const taskColumns = [
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: any = {
          pending: 'default',
          running: 'processing',
          completed: 'success',
          failed: 'error',
        };
        const icons: any = {
          pending: <SyncOutlined />,
          running: <SyncOutlined spin />,
          completed: <CheckCircleOutlined />,
          failed: <CloseCircleOutlined />,
        };
        return (
          <Tag color={colors[status]} icon={icons[status]}>
            {status === 'pending' && '等待中'}
            {status === 'running' && '运行中'}
            {status === 'completed' && '已完成'}
            {status === 'failed' && '失败'}
          </Tag>
        );
      },
    },
    {
      title: '总数',
      dataIndex: 'items_total',
      key: 'items_total',
    },
    {
      title: '成功',
      dataIndex: 'items_imported',
      key: 'items_imported',
      render: (count: number) => <span style={{ color: '#52c41a' }}>{count}</span>,
    },
    {
      title: '失败',
      dataIndex: 'items_failed',
      key: 'items_failed',
      render: (count: number) => count > 0 ? <span style={{ color: '#ff4d4f' }}>{count}</span> : count,
    },
    {
      title: '进度',
      key: 'progress',
      render: (_: any, record: ImportTask) => {
        if (record.items_total === 0) return '-';
        const percent = Math.round(
          ((record.items_imported + record.items_failed) / record.items_total) * 100
        );
        return <Progress percent={percent} size="small" />;
      },
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      key: 'started_at',
      render: (date: string | null) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      render: (date: string | null) => date ? new Date(date).toLocaleString() : '-',
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="外部平台导入"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新建配置
          </Button>
        }
      >
        <Tabs defaultActiveKey="url-import">
          <TabPane 
            tab={
              <span>
                <LinkOutlined />
                URL快速导入
              </span>
            } 
            key="url-import"
          >
            <Alert
              message="通过URL快速导入"
              description="支持从任何公开网页导入内容，包括：GitHub、CSDN、知乎、掘金、简书、Medium、个人博客等"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Card title="单个URL导入" style={{ marginBottom: 24 }}>
              <Form form={urlForm} layout="vertical" onFinish={handleUrlImport}>
                <Form.Item
                  name="url"
                  label="文章URL"
                  rules={[
                    { required: true, message: '请输入URL' },
                    { type: 'url', message: '请输入有效的URL' },
                  ]}
                >
                  <Input
                    prefix={<GlobalOutlined />}
                    placeholder="https://example.com/article"
                    size="large"
                  />
                </Form.Item>

                <Form.Item name="category" label="分类（可选）">
                  <Input placeholder="例如：技术文章" />
                </Form.Item>

                <Form.Item name="tags" label="标签（可选，用逗号分隔）">
                  <Input placeholder="例如：Python, 教程, 后端" />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<ImportOutlined />}
                    loading={urlImporting}
                    size="large"
                  >
                    立即导入
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            <Card title="批量URL导入">
              <Form form={batchUrlForm} layout="vertical" onFinish={handleBatchUrlImport}>
                <Form.Item
                  name="urls"
                  label="URL列表（每行一个）"
                  rules={[{ required: true, message: '请输入至少一个URL' }]}
                >
                  <TextArea
                    rows={6}
                    placeholder={`https://example.com/article1\nhttps://example.com/article2\nhttps://example.com/article3`}
                  />
                </Form.Item>

                <Form.Item name="batch_category" label="统一分类（可选）">
                  <Input placeholder="例如：技术文章" />
                </Form.Item>

                <Form.Item name="batch_tags" label="统一标签（可选，用逗号分隔）">
                  <Input placeholder="例如：Python, 教程" />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<ImportOutlined />}
                    loading={batchUrlImporting}
                    size="large"
                  >
                    批量导入
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            <Divider />

            <Card title="支持的网站类型" size="small">
              <List
                grid={{ gutter: 16, column: 3 }}
                dataSource={[
                  { name: 'GitHub', icon: '🐙', desc: 'README, Wiki等' },
                  { name: 'CSDN', icon: '📝', desc: '技术博客' },
                  { name: '知乎', icon: '🎓', desc: '专栏文章' },
                  { name: '掘金', icon: '💎', desc: '技术文章' },
                  { name: '简书', icon: '📖', desc: '个人文章' },
                  { name: 'Medium', icon: '✍️', desc: '英文博客' },
                  { name: '小红书', icon: '📕', desc: '公开笔记' },
                  { name: '个人博客', icon: '🌐', desc: '任何网页' },
                ]}
                renderItem={item => (
                  <List.Item>
                    <Card size="small">
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 32, marginBottom: 8 }}>{item.icon}</div>
                        <Title level={5} style={{ margin: 0 }}>{item.name}</Title>
                        <Text type="secondary" style={{ fontSize: 12 }}>{item.desc}</Text>
                      </div>
                    </Card>
                  </List.Item>
                )}
              />
            </Card>
          </TabPane>

          <TabPane tab="导入配置" key="configs">
            <Table
              columns={configColumns}
              dataSource={configs}
              rowKey="id"
              loading={loading}
            />
          </TabPane>
          
          <TabPane tab="导入任务" key="tasks">
            <Table
              columns={taskColumns}
              dataSource={tasks}
              rowKey="id"
            />
          </TabPane>
          
          <TabPane tab="支持的平台" key="platforms">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              {platforms.map(platform => (
                <Card key={platform.platform} size="small">
                  <Descriptions title={platform.name} column={1}>
                    <Descriptions.Item label="描述">{platform.description}</Descriptions.Item>
                    <Descriptions.Item label="必需配置">
                      {platform.required_config.join(', ')}
                    </Descriptions.Item>
                    {platform.optional_config.length > 0 && (
                      <Descriptions.Item label="可选配置">
                        {platform.optional_config.join(', ')}
                      </Descriptions.Item>
                    )}
                    <Descriptions.Item label="配置示例">
                      <pre style={{ background: '#f5f5f5', padding: '8px', borderRadius: '4px' }}>
                        {JSON.stringify(platform.example_config, null, 2)}
                      </pre>
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              ))}
            </Space>
          </TabPane>
        </Tabs>
      </Card>

      <Modal
        title={editingConfig ? '编辑导入配置' : '新建导入配置'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="配置名称"
            rules={[{ required: true, message: '请输入配置名称' }]}
          >
            <Input placeholder="例如：我的CSDN博客" />
          </Form.Item>

          <Form.Item
            name="platform"
            label="平台类型"
            rules={[{ required: true, message: '请选择平台类型' }]}
          >
            <Select placeholder="选择平台">
              {platforms.map(p => (
                <Select.Option key={p.platform} value={p.platform}>
                  {p.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="config"
            label="配置（JSON格式）"
            rules={[
              { required: true, message: '请输入配置' },
              {
                validator: (_, value) => {
                  try {
                    JSON.parse(value);
                    return Promise.resolve();
                  } catch {
                    return Promise.reject('请输入有效的JSON格式');
                  }
                },
              },
            ]}
          >
            <TextArea
              rows={6}
              placeholder='{"username": "your_username"}'
            />
          </Form.Item>

          <Form.Item name="auto_sync" label="自动同步" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item name="sync_interval" label="同步间隔（秒）">
            <Input type="number" placeholder="3600" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ImportManagementPage;
