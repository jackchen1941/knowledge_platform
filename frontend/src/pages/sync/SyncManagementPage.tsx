import React, { useEffect, useState } from 'react';
import {
  Card,
  Button,
  Table,
  Modal,
  Form,
  Input,
  Select,
  message,
  Space,
  Tag,
  Descriptions,
  Tabs,
  Alert,
  Statistic,
  Row,
  Col,
} from 'antd';
import {
  SyncOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CloudSyncOutlined,
  MobileOutlined,
  LaptopOutlined,
  DesktopOutlined,
} from '@ant-design/icons';
import api from '../../services/api';

const { TabPane } = Tabs;

interface Device {
  id: string;
  device_name: string;
  device_type: string;
  device_id: string;
  last_sync: string | null;
  is_active: boolean;
  created_at: string;
}

interface Conflict {
  id: string;
  entity_type: string;
  entity_id: string;
  device1_id: string;
  device2_id: string;
  device1_data: any;
  device2_data: any;
  created_at: string;
}

interface SyncStats {
  total_devices: number;
  active_devices: number;
  last_sync: string | null;
  pending_changes: number;
  unresolved_conflicts: number;
}

const SyncManagementPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [stats, setStats] = useState<SyncStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [conflictModalVisible, setConflictModalVisible] = useState(false);
  const [selectedConflict, setSelectedConflict] = useState<Conflict | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    await Promise.all([
      loadDevices(),
      loadConflicts(),
      loadStats(),
    ]);
  };

  const loadDevices = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/sync/devices');
      setDevices(response.data);
    } catch (error) {
      message.error('加载设备列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadConflicts = async () => {
    try {
      const response = await api.get('/api/v1/sync/conflicts');
      setConflicts(response.data);
    } catch (error) {
      message.error('加载冲突列表失败');
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/api/v1/sync/stats');
      setStats(response.data);
    } catch (error) {
      console.error('加载统计失败', error);
    }
  };

  const handleRegisterDevice = async (values: any) => {
    try {
      await api.post('/api/v1/sync/devices/register', {
        device_name: values.device_name,
        device_type: values.device_type,
        device_id: values.device_id || `device_${Date.now()}`,
      });
      message.success('设备注册成功');
      setModalVisible(false);
      form.resetFields();
      loadDevices();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败');
    }
  };

  const handleDeactivateDevice = async (deviceId: string) => {
    Modal.confirm({
      title: '确认停用',
      content: '确定要停用这个设备吗？',
      onOk: async () => {
        try {
          await api.delete(`/api/v1/sync/devices/${deviceId}`);
          message.success('设备已停用');
          loadDevices();
        } catch (error) {
          message.error('停用失败');
        }
      },
    });
  };

  const handleSync = async (deviceId: string) => {
    setSyncLoading(true);
    try {
      // Pull changes
      const pullResponse = await api.post('/api/v1/sync/pull', {
        device_id: deviceId,
      });
      
      message.success(`同步成功！`);
      loadData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '同步失败');
    } finally {
      setSyncLoading(false);
    }
  };

  const handleResolveConflict = async (conflictId: string, resolution: string) => {
    try {
      await api.post(`/api/v1/sync/conflicts/${conflictId}/resolve`, {
        resolution,
      });
      message.success('冲突已解决');
      setConflictModalVisible(false);
      setSelectedConflict(null);
      loadConflicts();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '解决失败');
    }
  };

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'mobile':
        return <MobileOutlined />;
      case 'desktop':
        return <DesktopOutlined />;
      default:
        return <LaptopOutlined />;
    }
  };

  const deviceColumns = [
    {
      title: '设备名称',
      dataIndex: 'device_name',
      key: 'device_name',
      render: (name: string, record: Device) => (
        <Space>
          {getDeviceIcon(record.device_type)}
          {name}
        </Space>
      ),
    },
    {
      title: '设备类型',
      dataIndex: 'device_type',
      key: 'device_type',
      render: (type: string) => {
        const typeMap: any = {
          web: '网页',
          mobile: '移动端',
          desktop: '桌面端',
        };
        return typeMap[type] || type;
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'default'}>
          {active ? '活跃' : '已停用'}
        </Tag>
      ),
    },
    {
      title: '最后同步',
      dataIndex: 'last_sync',
      key: 'last_sync',
      render: (date: string | null) => date ? new Date(date).toLocaleString() : '从未',
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: Device) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<SyncOutlined />}
            onClick={() => handleSync(record.id)}
            loading={syncLoading}
          >
            同步
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDeactivateDevice(record.id)}
          >
            停用
          </Button>
        </Space>
      ),
    },
  ];

  const conflictColumns = [
    {
      title: '实体类型',
      dataIndex: 'entity_type',
      key: 'entity_type',
      render: (type: string) => {
        const typeMap: any = {
          knowledge: '知识条目',
          category: '分类',
          tag: '标签',
        };
        return typeMap[type] || type;
      },
    },
    {
      title: '设备1',
      dataIndex: 'device1_id',
      key: 'device1_id',
    },
    {
      title: '设备2',
      dataIndex: 'device2_id',
      key: 'device2_id',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: Conflict) => (
        <Button
          size="small"
          onClick={() => {
            setSelectedConflict(record);
            setConflictModalVisible(true);
          }}
        >
          解决
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* Statistics */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总设备数"
                value={stats.total_devices}
                prefix={<CloudSyncOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="活跃设备"
                value={stats.active_devices}
                valueStyle={{ color: '#3f8600' }}
                prefix={<CheckCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="待处理冲突"
                value={stats.unresolved_conflicts}
                valueStyle={{ color: stats.unresolved_conflicts > 0 ? '#cf1322' : '#3f8600' }}
                prefix={<CloseCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="最后同步"
                value={stats.last_sync ? new Date(stats.last_sync).toLocaleString() : '从未'}
              />
            </Card>
          </Col>
        </Row>
      )}

      <Card
        title="多设备同步"
        extra={
          <Button
            type="primary"
            icon={<SyncOutlined />}
            onClick={() => setModalVisible(true)}
          >
            注册设备
          </Button>
        }
      >
        {conflicts.length > 0 && (
          <Alert
            message="存在同步冲突"
            description={`有 ${conflicts.length} 个冲突需要解决`}
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        <Tabs defaultActiveKey="devices">
          <TabPane tab="设备列表" key="devices">
            <Table
              columns={deviceColumns}
              dataSource={devices}
              rowKey="id"
              loading={loading}
            />
          </TabPane>

          <TabPane tab={`冲突 (${conflicts.length})`} key="conflicts">
            <Table
              columns={conflictColumns}
              dataSource={conflicts}
              rowKey="id"
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* Register Device Modal */}
      <Modal
        title="注册设备"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleRegisterDevice}>
          <Form.Item
            name="device_name"
            label="设备名称"
            rules={[{ required: true, message: '请输入设备名称' }]}
          >
            <Input placeholder="例如：我的笔记本" />
          </Form.Item>

          <Form.Item
            name="device_type"
            label="设备类型"
            rules={[{ required: true, message: '请选择设备类型' }]}
          >
            <Select placeholder="选择设备类型">
              <Select.Option value="web">网页</Select.Option>
              <Select.Option value="mobile">移动端</Select.Option>
              <Select.Option value="desktop">桌面端</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="device_id"
            label="设备ID（可选）"
            help="留空将自动生成"
          >
            <Input placeholder="自动生成" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Conflict Resolution Modal */}
      <Modal
        title="解决冲突"
        open={conflictModalVisible}
        onCancel={() => {
          setConflictModalVisible(false);
          setSelectedConflict(null);
        }}
        footer={null}
        width={800}
      >
        {selectedConflict && (
          <div>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="实体类型">
                {selectedConflict.entity_type}
              </Descriptions.Item>
              <Descriptions.Item label="实体ID">
                {selectedConflict.entity_id}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 24 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Card
                    title={`设备1数据 (${selectedConflict.device1_id})`}
                    size="small"
                  >
                    <pre style={{ maxHeight: 200, overflow: 'auto' }}>
                      {JSON.stringify(selectedConflict.device1_data, null, 2)}
                    </pre>
                    <Button
                      type="primary"
                      block
                      style={{ marginTop: 8 }}
                      onClick={() => handleResolveConflict(selectedConflict.id, 'device1')}
                    >
                      使用此版本
                    </Button>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card
                    title={`设备2数据 (${selectedConflict.device2_id})`}
                    size="small"
                  >
                    <pre style={{ maxHeight: 200, overflow: 'auto' }}>
                      {JSON.stringify(selectedConflict.device2_data, null, 2)}
                    </pre>
                    <Button
                      type="primary"
                      block
                      style={{ marginTop: 8 }}
                      onClick={() => handleResolveConflict(selectedConflict.id, 'device2')}
                    >
                      使用此版本
                    </Button>
                  </Card>
                </Col>
              </Row>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default SyncManagementPage;
