import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';

import { useAppSelector } from '@/hooks/redux';
import { selectIsAuthenticated } from '@/store/slices/authSlice';

// Layout components
import AppHeader from '@/components/layout/AppHeader';
import AppSidebar from '@/components/layout/AppSidebar';

// Pages
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import KnowledgePage from '@/pages/knowledge/KnowledgePage';
import KnowledgeGraphPage from '@/pages/knowledge/KnowledgeGraphPage';
import CategoriesPage from '@/pages/categories/CategoriesPage';
import TagsPage from '@/pages/tags/TagsPage';
import SearchPage from '@/pages/search/SearchPage';
import AnalyticsPage from '@/pages/analytics/AnalyticsPage';
import SettingsPage from '@/pages/settings/SettingsPage';
import ImportManagementPage from '@/pages/import/ImportManagementPage';
import SyncManagementPage from '@/pages/sync/SyncManagementPage';
import NotificationsPage from '@/pages/notifications/NotificationsPage';
import WebSocketTestPage from '@/pages/websocket/WebSocketTestPage';

const { Content } = Layout;

const App: React.FC = () => {
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppHeader />
      <Layout>
        <AppSidebar />
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff',
              borderRadius: 8,
            }}
          >
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/knowledge/*" element={<KnowledgePage />} />
              <Route path="/graph" element={<KnowledgeGraphPage />} />
              <Route path="/categories" element={<CategoriesPage />} />
              <Route path="/tags" element={<TagsPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/import" element={<ImportManagementPage />} />
              <Route path="/sync" element={<SyncManagementPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
              <Route path="/websocket-test" element={<WebSocketTestPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default App;