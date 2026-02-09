import React from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  FolderOutlined,
  TagsOutlined,
  SearchOutlined,
  BarChartOutlined,
  SettingOutlined,
  ApartmentOutlined,
  ImportOutlined,
  SyncOutlined,
  BellOutlined,
  WifiOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Sider } = Layout;

const AppSidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/knowledge',
      icon: <FileTextOutlined />,
      label: '知识库',
    },
    {
      key: '/graph',
      icon: <ApartmentOutlined />,
      label: '知识图谱',
    },
    {
      key: '/categories',
      icon: <FolderOutlined />,
      label: '分类管理',
    },
    {
      key: '/tags',
      icon: <TagsOutlined />,
      label: '标签管理',
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: '搜索',
    },
    {
      key: '/import',
      icon: <ImportOutlined />,
      label: '外部导入',
    },
    {
      key: '/sync',
      icon: <SyncOutlined />,
      label: '多设备同步',
    },
    {
      key: '/notifications',
      icon: <BellOutlined />,
      label: '通知中心',
    },
    {
      key: '/websocket-test',
      icon: <WifiOutlined />,
      label: 'WebSocket测试',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '统计分析',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  // Get current selected key based on pathname
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path === '/') return '/';
    const matchedItem = menuItems.find(item => path.startsWith(item.key));
    return matchedItem ? matchedItem.key : '/';
  };

  return (
    <Sider
      width={220}
      style={{
        background: '#fff',
        boxShadow: '2px 0 8px rgba(0,0,0,0.06)',
      }}
    >
      <Menu
        mode="inline"
        selectedKeys={[getSelectedKey()]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ height: '100%', borderRight: 0, paddingTop: '16px' }}
      />
    </Sider>
  );
};

export default AppSidebar;
