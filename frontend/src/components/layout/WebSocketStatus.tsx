import React from 'react';
import { Badge, Tooltip, Button, Space, Popover, Typography, Divider } from 'antd';
import {
  WifiOutlined,
  DisconnectOutlined,
  LoadingOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

interface WebSocketStatusProps {
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  onReconnect: () => void;
  connectionStats?: any;
  lastMessage?: any;
}

const WebSocketStatus: React.FC<WebSocketStatusProps> = ({
  isConnected,
  connectionStatus,
  onReconnect,
  connectionStats,
  lastMessage
}) => {
  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <WifiOutlined style={{ color: '#52c41a' }} />;
      case 'connecting':
        return <LoadingOutlined style={{ color: '#1890ff' }} />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <DisconnectOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return '实时连接已建立';
      case 'connecting':
        return '正在连接...';
      case 'error':
        return '连接错误';
      default:
        return '未连接';
    }
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'success';
      case 'connecting':
        return 'processing';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const statusContent = (
    <div style={{ width: '300px' }}>
      <Title level={5}>
        <InfoCircleOutlined /> 实时连接状态
      </Title>
      
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text strong>状态: </Text>
          <Badge status={getStatusColor()} text={getStatusText()} />
        </div>
        
        {connectionStats && (
          <>
            <Divider style={{ margin: '8px 0' }} />
            <div>
              <Text strong>连接统计:</Text>
              <div style={{ marginTop: '8px', fontSize: '12px' }}>
                <div>总连接数: {connectionStats.total_connections}</div>
                <div>在线用户: {connectionStats.total_users}</div>
                <div>活跃房间: {connectionStats.total_rooms}</div>
              </div>
            </div>
          </>
        )}
        
        {lastMessage && (
          <>
            <Divider style={{ margin: '8px 0' }} />
            <div>
              <Text strong>最后消息:</Text>
              <div style={{ marginTop: '8px', fontSize: '12px' }}>
                <div>类型: {lastMessage.type}</div>
                {lastMessage.timestamp && (
                  <div>时间: {new Date(lastMessage.timestamp).toLocaleTimeString()}</div>
                )}
              </div>
            </div>
          </>
        )}
        
        <Divider style={{ margin: '8px 0' }} />
        
        <Space>
          <Button 
            size="small" 
            icon={<ReloadOutlined />} 
            onClick={onReconnect}
            disabled={connectionStatus === 'connecting'}
          >
            重新连接
          </Button>
        </Space>
        
        <div style={{ fontSize: '11px', color: '#999', marginTop: '8px' }}>
          实时连接用于接收通知、同步更新和系统消息
        </div>
      </Space>
    </div>
  );

  return (
    <Popover 
      content={statusContent} 
      title={null}
      trigger="hover"
      placement="bottomRight"
    >
      <div style={{ cursor: 'pointer', padding: '4px 8px' }}>
        <Tooltip title={getStatusText()}>
          <Badge 
            status={getStatusColor()} 
            dot={connectionStatus === 'connecting'}
          >
            {getStatusIcon()}
          </Badge>
        </Tooltip>
      </div>
    </Popover>
  );
};

export default WebSocketStatus;