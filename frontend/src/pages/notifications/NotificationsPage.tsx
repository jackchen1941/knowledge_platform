import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Badge,
  Button,
  Typography,
  Space,
  Tag,
  Dropdown,
  Menu,
  Modal,
  Statistic,
  Row,
  Col,
  Empty,
  Spin,
  message,
  Tabs,
  Switch,
  Form,
  Select
} from 'antd';
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  SettingOutlined,
  FilterOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { confirm } = Modal;

interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: 'info' | 'success' | 'warning' | 'error';
  category: 'sync' | 'knowledge' | 'system' | 'import';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  is_read: boolean;
  is_archived: boolean;
  action_url?: string;
  action_data?: Record<string, any>;
  created_at: string;
  read_at?: string;
  expires_at?: string;
}

interface NotificationStats {
  total: number;
  unread: number;
  categories: Record<string, number>;
}

interface NotificationPreference {
  id: string;
  category: string;
  enabled: boolean;
  in_app: boolean;
  email: boolean;
  push: boolean;
  min_priority: string;
}

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<NotificationStats>({ total: 0, unread: 0, categories: {} });
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const [preferencesVisible, setPreferencesVisible] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    loadNotifications();
    loadStats();
    loadPreferences();
  }, [selectedCategory, showUnreadOnly]);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      // Mock API call
      const mockNotifications: Notification[] = [
        {
          id: '1',
          title: '同步完成',
          message: '设备 MacBook Pro 同步完成，处理了 5 个变更。',
          notification_type: 'success',
          category: 'sync',
          priority: 'normal',
          is_read: false,
          is_archived: false,
          action_url: '/sync',
          action_data: { device_id: 'device-1' },
          created_at: '2026-02-09T20:30:00Z'
        },
        {
          id: '2',
          title: '新知识条目',
          message: '知识条目 "React Hooks 最佳实践" 已创建。',
          notification_type: 'info',
          category: 'knowledge',
          priority: 'normal',
          is_read: false,
          is_archived: false,
          action_url: '/knowledge/123',
          action_data: { knowledge_id: '123' },
          created_at: '2026-02-09T19:45:00Z'
        },
        {
          id: '3',
          title: '同步冲突',
          message: '设备 iPhone 同步时发现 2 个冲突，需要手动解决。',
          notification_type: 'warning',
          category: 'sync',
          priority: 'high',
          is_read: true,
          is_archived: false,
          action_url: '/sync',
          action_data: { conflicts: 2 },
          created_at: '2026-02-09T18:20:00Z',
          read_at: '2026-02-09T19:00:00Z'
        },
        {
          id: '4',
          title: '导入完成',
          message: '从 CSDN 导入完成，成功导入 12 个条目。',
          notification_type: 'success',
          category: 'import',
          priority: 'normal',
          is_read: true,
          is_archived: false,
          created_at: '2026-02-09T17:30:00Z',
          read_at: '2026-02-09T18:00:00Z'
        }
      ];

      let filteredNotifications = mockNotifications;
      
      if (selectedCategory) {
        filteredNotifications = filteredNotifications.filter(n => n.category === selectedCategory);
      }
      
      if (showUnreadOnly) {
        filteredNotifications = filteredNotifications.filter(n => !n.is_read);
      }

      setNotifications(filteredNotifications);
    } catch (error) {
      message.error('加载通知失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      // Mock stats
      setStats({
        total: 4,
        unread: 2,
        categories: {
          sync: 1,
          knowledge: 1,
          system: 0,
          import: 0
        }
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadPreferences = async () => {
    try {
      // Mock preferences
      const mockPreferences: NotificationPreference[] = [
        {
          id: '1',
          category: 'sync',
          enabled: true,
          in_app: true,
          email: false,
          push: false,
          min_priority: 'normal'
        },
        {
          id: '2',
          category: 'knowledge',
          enabled: true,
          in_app: true,
          email: true,
          push: false,
          min_priority: 'normal'
        },
        {
          id: '3',
          category: 'system',
          enabled: true,
          in_app: true,
          email: false,
          push: false,
          min_priority: 'high'
        },
        {
          id: '4',
          category: 'import',
          enabled: true,
          in_app: true,
          email: true,
          push: false,
          min_priority: 'normal'
        }
      ];
      setPreferences(mockPreferences);
    } catch (error) {
      console.error('Failed to load preferences:', error);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      // Mock API call
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId 
            ? { ...n, is_read: true, read_at: new Date().toISOString() }
            : n
        )
      );
      message.success('已标记为已读');
      loadStats();
    } catch (error) {
      message.error('标记失败');
    }
  };

  const markAllAsRead = async () => {
    try {
      // Mock API call
      setNotifications(prev => 
        prev.map(n => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
      );
      message.success('已全部标记为已读');
      loadStats();
    } catch (error) {
      message.error('标记失败');
    }
  };

  const archiveNotification = async (notificationId: string) => {
    try {
      // Mock API call
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      message.success('通知已归档');
      loadStats();
    } catch (error) {
      message.error('归档失败');
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'sync':
        return 'blue';
      case 'knowledge':
        return 'green';
      case 'system':
        return 'orange';
      case 'import':
        return 'purple';
      default:
        return 'default';
    }
  };

  const getCategoryName = (category: string) => {
    switch (category) {
      case 'sync':
        return '同步';
      case 'knowledge':
        return '知识库';
      case 'system':
        return '系统';
      case 'import':
        return '导入';
      default:
        return category;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return '#ff4d4f';
      case 'high':
        return '#faad14';
      case 'normal':
        return '#1890ff';
      case 'low':
        return '#52c41a';
      default:
        return '#d9d9d9';
    }
  };

  const filterMenu = (
    <Menu>
      <Menu.Item key="all" onClick={() => setSelectedCategory(undefined)}>
        全部通知
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="sync" onClick={() => setSelectedCategory('sync')}>
        同步通知
      </Menu.Item>
      <Menu.Item key="knowledge" onClick={() => setSelectedCategory('knowledge')}>
        知识库通知
      </Menu.Item>
      <Menu.Item key="system" onClick={() => setSelectedCategory('system')}>
        系统通知
      </Menu.Item>
      <Menu.Item key="import" onClick={() => setSelectedCategory('import')}>
        导入通知
      </Menu.Item>
    </Menu>
  );

  const actionMenu = (notification: Notification) => (
    <Menu>
      {!notification.is_read && (
        <Menu.Item key="read" onClick={() => markAsRead(notification.id)}>
          <CheckOutlined /> 标记为已读
        </Menu.Item>
      )}
      <Menu.Item key="archive" onClick={() => archiveNotification(notification.id)}>
        <DeleteOutlined /> 归档
      </Menu.Item>
    </Menu>
  );

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <BellOutlined /> 通知中心
        </Title>
        <Paragraph type="secondary">
          管理您的通知和偏好设置
        </Paragraph>
      </div>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总通知"
              value={stats.total}
              prefix={<BellOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="未读通知"
              value={stats.unread}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="同步通知"
              value={stats.categories.sync || 0}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="知识库通知"
              value={stats.categories.knowledge || 0}
              prefix={<InfoCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="通知列表" key="all">
          <Card>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                <Dropdown overlay={filterMenu} trigger={['click']}>
                  <Button icon={<FilterOutlined />}>
                    {selectedCategory ? getCategoryName(selectedCategory) : '全部分类'}
                  </Button>
                </Dropdown>
                <Switch
                  checkedChildren="仅未读"
                  unCheckedChildren="全部"
                  checked={showUnreadOnly}
                  onChange={setShowUnreadOnly}
                />
              </Space>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={loadNotifications}>
                  刷新
                </Button>
                <Button 
                  type="primary" 
                  icon={<CheckOutlined />} 
                  onClick={markAllAsRead}
                  disabled={stats.unread === 0}
                >
                  全部已读
                </Button>
                <Button 
                  icon={<SettingOutlined />} 
                  onClick={() => setPreferencesVisible(true)}
                >
                  偏好设置
                </Button>
              </Space>
            </div>

            <Spin spinning={loading}>
              {notifications.length === 0 ? (
                <Empty description="暂无通知" />
              ) : (
                <List
                  itemLayout="vertical"
                  dataSource={notifications}
                  renderItem={(notification) => (
                    <List.Item
                      key={notification.id}
                      style={{
                        backgroundColor: notification.is_read ? '#fafafa' : '#fff',
                        border: '1px solid #f0f0f0',
                        borderRadius: '8px',
                        marginBottom: '8px',
                        padding: '16px'
                      }}
                      actions={[
                        <Dropdown overlay={actionMenu(notification)} trigger={['click']}>
                          <Button type="text" size="small">
                            操作
                          </Button>
                        </Dropdown>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={getNotificationIcon(notification.notification_type)}
                        title={
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontWeight: notification.is_read ? 'normal' : 'bold' }}>
                              {notification.title}
                            </span>
                            {!notification.is_read && (
                              <Badge status="processing" />
                            )}
                            <Tag color={getCategoryColor(notification.category)}>
                              {getCategoryName(notification.category)}
                            </Tag>
                            <div
                              style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                backgroundColor: getPriorityColor(notification.priority)
                              }}
                            />
                          </div>
                        }
                        description={
                          <div>
                            <Paragraph style={{ margin: 0 }}>
                              {notification.message}
                            </Paragraph>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                              {new Date(notification.created_at).toLocaleString()}
                              {notification.read_at && (
                                <span> • 已读于 {new Date(notification.read_at).toLocaleString()}</span>
                              )}
                            </Text>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </Spin>
          </Card>
        </TabPane>

        <TabPane tab="偏好设置" key="preferences">
          <Card title="通知偏好设置">
            <List
              dataSource={preferences}
              renderItem={(pref) => (
                <List.Item>
                  <List.Item.Meta
                    title={getCategoryName(pref.category)}
                    description={
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div>
                          <Text>启用通知: </Text>
                          <Switch checked={pref.enabled} size="small" />
                        </div>
                        <div>
                          <Text>应用内: </Text>
                          <Switch checked={pref.in_app} size="small" />
                          <Text style={{ marginLeft: '16px' }}>邮件: </Text>
                          <Switch checked={pref.email} size="small" />
                          <Text style={{ marginLeft: '16px' }}>推送: </Text>
                          <Switch checked={pref.push} size="small" />
                        </div>
                        <div>
                          <Text>最低优先级: </Text>
                          <Select value={pref.min_priority} size="small" style={{ width: '80px' }}>
                            <Select.Option value="low">低</Select.Option>
                            <Select.Option value="normal">普通</Select.Option>
                            <Select.Option value="high">高</Select.Option>
                            <Select.Option value="urgent">紧急</Select.Option>
                          </Select>
                        </div>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* Preferences Modal */}
      <Modal
        title="通知偏好设置"
        visible={preferencesVisible}
        onCancel={() => setPreferencesVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setPreferencesVisible(false)}>
            取消
          </Button>,
          <Button key="save" type="primary" onClick={() => setPreferencesVisible(false)}>
            保存
          </Button>
        ]}
        width={600}
      >
        <Form layout="vertical">
          {preferences.map((pref) => (
            <Card key={pref.id} size="small" style={{ marginBottom: '16px' }}>
              <Title level={5}>{getCategoryName(pref.category)}</Title>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="启用通知">
                    <Switch checked={pref.enabled} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="最低优先级">
                    <Select value={pref.min_priority} style={{ width: '100%' }}>
                      <Select.Option value="low">低</Select.Option>
                      <Select.Option value="normal">普通</Select.Option>
                      <Select.Option value="high">高</Select.Option>
                      <Select.Option value="urgent">紧急</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="应用内">
                    <Switch checked={pref.in_app} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="邮件">
                    <Switch checked={pref.email} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="推送">
                    <Switch checked={pref.push} />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          ))}
        </Form>
      </Modal>
    </div>
  );
};

export default NotificationsPage;