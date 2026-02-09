import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, Typography, Badge } from 'antd';
import {
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  BellOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import { logout, selectCurrentUser } from '@/store/slices/authSlice';
import { useWebSocket } from '@/hooks/useWebSocket';
import WebSocketStatus from './WebSocketStatus';

const { Header } = Layout;
const { Text } = Typography;

const AppHeader: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const currentUser = useAppSelector(selectCurrentUser);

  // WebSocket connection for real-time features
  const {
    isConnected,
    connectionStatus,
    reconnect,
    connectionStats,
    lastMessage
  } = useWebSocket(
    currentUser?.id || 'demo-user', // Use demo user for testing
    'demo-token', // Use demo token for testing
    {
      onMessage: (message) => {
        console.log('WebSocket message received:', message);
      },
      onConnect: () => {
        console.log('WebSocket connected in header');
      },
      onDisconnect: () => {
        console.log('WebSocket disconnected in header');
      }
    }
  );

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
      onClick: () => navigate('/settings'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <Header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#fff',
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div
          style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#1890ff',
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          📚 知识管理平台
        </div>
      </div>

      <Space size="large">
        <Badge dot={!isConnected} offset={[-2, 2]}>
          <BellOutlined 
            style={{ fontSize: '18px', cursor: 'pointer' }} 
            onClick={() => navigate('/notifications')}
          />
        </Badge>
        
        <WebSocketStatus
          isConnected={isConnected}
          connectionStatus={connectionStatus}
          onReconnect={reconnect}
          connectionStats={connectionStats}
          lastMessage={lastMessage}
        />
        
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} />
            <Text>{currentUser?.username || currentUser?.email || '用户'}</Text>
          </Space>
        </Dropdown>
      </Space>
    </Header>
  );
};

export default AppHeader;
