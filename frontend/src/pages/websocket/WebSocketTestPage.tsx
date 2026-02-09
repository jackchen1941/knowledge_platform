import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Input,
  Select,
  Form,
  List,
  Tag,
  Divider,
  Row,
  Col,
  Statistic,
  Alert,
  Badge,
  message
} from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  ReloadOutlined,
  WifiOutlined,
  DisconnectOutlined,
  BellOutlined,
  SyncOutlined,
  MessageOutlined
} from '@ant-design/icons';
import { useWebSocket } from '@/hooks/useWebSocket';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface TestMessage {
  id: string;
  type: string;
  data?: any;
  timestamp: string;
  direction: 'sent' | 'received';
}

const WebSocketTestPage: React.FC = () => {
  const [messages, setMessages] = useState<TestMessage[]>([]);
  const [form] = Form.useForm();

  const {
    isConnected,
    connectionStatus,
    sendMessage,
    subscribe,
    unsubscribe,
    reconnect,
    disconnect,
    lastMessage,
    connectionStats
  } = useWebSocket(
    'test-user-123',
    'test-token-456',
    {
      onMessage: (message) => {
        const testMessage: TestMessage = {
          id: Date.now().toString(),
          type: message.type,
          data: message.data,
          timestamp: new Date().toISOString(),
          direction: 'received'
        };
        setMessages(prev => [testMessage, ...prev]);
      },
      onConnect: () => {
        message.success('WebSocket 连接成功');
      },
      onDisconnect: () => {
        message.warning('WebSocket 连接断开');
      },
      onError: () => {
        message.error('WebSocket 连接错误');
      }
    }
  );

  const handleSendMessage = (values: any) => {
    const messageData = {
      type: values.type,
      ...values.data && { data: JSON.parse(values.data) },
      ...values.room && { room: values.room }
    };

    sendMessage(messageData);

    const testMessage: TestMessage = {
      id: Date.now().toString(),
      type: values.type,
      data: messageData,
      timestamp: new Date().toISOString(),
      direction: 'sent'
    };
    setMessages(prev => [testMessage, ...prev]);

    message.success('消息已发送');
  };

  const handleClearMessages = () => {
    setMessages([]);
    message.info('消息列表已清空');
  };

  const handleSendTestNotification = async () => {
    try {
      const response = await fetch('/api/v1/notifications/demo', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test-token-456',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        message.success('测试通知已发送');
      } else {
        message.error('发送测试通知失败');
      }
    } catch (error) {
      message.error('发送测试通知失败');
    }
  };

  const getMessageTypeColor = (type: string) => {
    switch (type) {
      case 'notification':
        return 'blue';
      case 'sync_update':
        return 'green';
      case 'system_message':
        return 'orange';
      case 'error':
        return 'red';
      case 'ping':
      case 'pong':
        return 'gray';
      default:
        return 'default';
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'notification':
        return <BellOutlined />;
      case 'sync_update':
        return <SyncOutlined />;
      case 'system_message':
        return <MessageOutlined />;
      default:
        return <MessageOutlined />;
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <WifiOutlined /> WebSocket 测试页面
      </Title>
      <Paragraph type="secondary">
        测试实时WebSocket连接和消息传递功能
      </Paragraph>

      {/* Connection Status */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="连接状态"
              value={connectionStatus}
              prefix={isConnected ? <WifiOutlined style={{ color: '#52c41a' }} /> : <DisconnectOutlined />}
              valueStyle={{ color: isConnected ? '#52c41a' : '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="消息数量"
              value={messages.length}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总连接数"
              value={connectionStats?.total_connections || 0}
              prefix={<WifiOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="在线用户"
              value={connectionStats?.total_users || 0}
              prefix={<BellOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* Message Sender */}
        <Col span={12}>
          <Card title="发送消息" style={{ height: '600px' }}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSendMessage}
              initialValues={{ type: 'ping' }}
            >
              <Form.Item
                name="type"
                label="消息类型"
                rules={[{ required: true, message: '请选择消息类型' }]}
              >
                <Select>
                  <Option value="ping">Ping</Option>
                  <Option value="subscribe">订阅房间</Option>
                  <Option value="unsubscribe">取消订阅</Option>
                  <Option value="get_stats">获取统计</Option>
                  <Option value="custom">自定义</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="room"
                label="房间名称"
                help="仅用于订阅/取消订阅消息"
              >
                <Input placeholder="例如: notifications, sync_updates" />
              </Form.Item>

              <Form.Item
                name="data"
                label="消息数据 (JSON)"
                help="可选的JSON格式数据"
              >
                <TextArea
                  rows={4}
                  placeholder='{"key": "value"}'
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<SendOutlined />}
                    disabled={!isConnected}
                  >
                    发送消息
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={reconnect}
                  >
                    重新连接
                  </Button>
                  <Button
                    danger
                    onClick={disconnect}
                  >
                    断开连接
                  </Button>
                </Space>
              </Form.Item>
            </Form>

            <Divider />

            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="dashed"
                icon={<BellOutlined />}
                onClick={handleSendTestNotification}
                block
              >
                发送测试通知
              </Button>
              
              <Button
                onClick={() => subscribe('notifications')}
                disabled={!isConnected}
                block
              >
                订阅通知房间
              </Button>
              
              <Button
                onClick={() => subscribe('sync_updates')}
                disabled={!isConnected}
                block
              >
                订阅同步更新房间
              </Button>
            </Space>
          </Card>
        </Col>

        {/* Message History */}
        <Col span={12}>
          <Card 
            title="消息历史" 
            style={{ height: '600px' }}
            extra={
              <Button
                size="small"
                icon={<ClearOutlined />}
                onClick={handleClearMessages}
              >
                清空
              </Button>
            }
          >
            <div style={{ height: '500px', overflowY: 'auto' }}>
              {messages.length === 0 ? (
                <Alert
                  message="暂无消息"
                  description="发送消息或等待接收消息"
                  type="info"
                  showIcon
                />
              ) : (
                <List
                  dataSource={messages}
                  renderItem={(item) => (
                    <List.Item
                      style={{
                        backgroundColor: item.direction === 'sent' ? '#f6ffed' : '#fff7e6',
                        border: '1px solid #f0f0f0',
                        borderRadius: '8px',
                        marginBottom: '8px',
                        padding: '12px'
                      }}
                    >
                      <List.Item.Meta
                        avatar={
                          <Badge
                            status={item.direction === 'sent' ? 'success' : 'processing'}
                            dot
                          />
                        }
                        title={
                          <Space>
                            {getMessageIcon(item.type)}
                            <Tag color={getMessageTypeColor(item.type)}>
                              {item.type}
                            </Tag>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                              {item.direction === 'sent' ? '发送' : '接收'}
                            </Text>
                          </Space>
                        }
                        description={
                          <div>
                            {item.data && (
                              <pre style={{ 
                                fontSize: '12px', 
                                margin: '4px 0',
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word'
                              }}>
                                {JSON.stringify(item.data, null, 2)}
                              </pre>
                            )}
                            <Text type="secondary" style={{ fontSize: '11px' }}>
                              {new Date(item.timestamp).toLocaleString()}
                            </Text>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default WebSocketTestPage;