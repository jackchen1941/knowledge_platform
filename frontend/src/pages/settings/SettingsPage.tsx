import React, { useState } from 'react';
import {
  Card,
  Tabs,
  Form,
  Input,
  Button,
  message,
  Space,
  Typography,
  Divider,
  Select,
  Switch,
  Upload,
  Progress,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  SettingOutlined,
  ExportOutlined,
  ImportOutlined,
  UploadOutlined,
  CloudDownloadOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons';
import { authAPI, backupAPI } from '@/services/api';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

const SettingsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [backupLoading, setBackupLoading] = useState(false);
  const [restoreLoading, setRestoreLoading] = useState(false);
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const handleProfileUpdate = async (values: any) => {
    setLoading(true);
    try {
      // TODO: Implement profile update API
      message.success('个人资料更新成功');
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      message.error('更新失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (values: any) => {
    setLoading(true);
    try {
      // TODO: Implement password change API
      message.success('密码修改成功');
      passwordForm.resetFields();
    } catch (error: any) {
      console.error('Failed to change password:', error);
      message.error('修改失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      message.info(`正在导出为 ${format} 格式...`);
      // TODO: Implement export functionality
      message.success('导出成功');
    } catch (error: any) {
      console.error('Export failed:', error);
      message.error('导出失败');
    }
  };

  const handleCreateBackup = async () => {
    setBackupLoading(true);
    try {
      const response = await backupAPI.create('full');
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `backup_${new Date().toISOString().split('T')[0]}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('备份创建成功');
    } catch (error: any) {
      console.error('Backup failed:', error);
      message.error('备份失败');
    } finally {
      setBackupLoading(false);
    }
  };

  const handleRestoreBackup = async (file: File) => {
    setRestoreLoading(true);
    try {
      // Verify backup first
      const verifyResponse = await backupAPI.verify(file);
      
      if (!verifyResponse.data.valid) {
        message.error(`备份文件无效: ${verifyResponse.data.error}`);
        return;
      }
      
      message.info(`备份文件有效，包含 ${verifyResponse.data.item_count} 条知识`);
      
      // Restore backup
      const options = {
        restore_knowledge: true,
        restore_categories: true,
        restore_tags: true,
        overwrite_existing: false,
      };
      
      const restoreResponse = await backupAPI.restore(file, options);
      
      message.success(
        `恢复成功！知识: ${restoreResponse.data.knowledge_items_restored}, ` +
        `分类: ${restoreResponse.data.categories_restored}, ` +
        `标签: ${restoreResponse.data.tags_restored}`
      );
    } catch (error: any) {
      console.error('Restore failed:', error);
      message.error('恢复失败');
    } finally {
      setRestoreLoading(false);
    }
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        设置
      </Title>

      <Tabs defaultActiveKey="profile">
        {/* Profile Settings */}
        <TabPane
          tab={
            <span>
              <UserOutlined />
              个人资料
            </span>
          }
          key="profile"
        >
          <Card>
            <Form
              form={profileForm}
              layout="vertical"
              onFinish={handleProfileUpdate}
              style={{ maxWidth: 600 }}
            >
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
                name="bio"
                label="个人简介"
              >
                <Input.TextArea
                  placeholder="介绍一下自己（可选）"
                  rows={4}
                />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  保存更改
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        {/* Security Settings */}
        <TabPane
          tab={
            <span>
              <LockOutlined />
              安全设置
            </span>
          }
          key="security"
        >
          <Card title="修改密码">
            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={handlePasswordChange}
              style={{ maxWidth: 600 }}
            >
              <Form.Item
                name="current_password"
                label="当前密码"
                rules={[{ required: true, message: '请输入当前密码' }]}
              >
                <Input.Password placeholder="输入当前密码" />
              </Form.Item>

              <Form.Item
                name="new_password"
                label="新密码"
                rules={[
                  { required: true, message: '请输入新密码' },
                  { min: 6, message: '密码至少6个字符' },
                ]}
              >
                <Input.Password placeholder="输入新密码" />
              </Form.Item>

              <Form.Item
                name="confirm_password"
                label="确认新密码"
                dependencies={['new_password']}
                rules={[
                  { required: true, message: '请确认新密码' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('new_password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('两次输入的密码不一致'));
                    },
                  }),
                ]}
              >
                <Input.Password placeholder="再次输入新密码" />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  修改密码
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        {/* System Settings */}
        <TabPane
          tab={
            <span>
              <SettingOutlined />
              系统设置
            </span>
          }
          key="system"
        >
          <Card title="偏好设置">
            <Form layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item
                name="theme"
                label="主题"
                initialValue="light"
              >
                <Select>
                  <Select.Option value="light">浅色</Select.Option>
                  <Select.Option value="dark">深色</Select.Option>
                  <Select.Option value="auto">跟随系统</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="language"
                label="语言"
                initialValue="zh-CN"
              >
                <Select>
                  <Select.Option value="zh-CN">简体中文</Select.Option>
                  <Select.Option value="en-US">English</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="auto_save"
                label="自动保存"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item>
                <Button type="primary">
                  保存设置
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        {/* Import/Export */}
        <TabPane
          tab={
            <span>
              <ExportOutlined />
              导入导出
            </span>
          }
          key="import-export"
        >
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card title="数据备份">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text>创建完整数据备份，包含所有知识条目、分类、标签和关联关系。</Text>
                </div>
                <Button
                  type="primary"
                  icon={<CloudDownloadOutlined />}
                  onClick={handleCreateBackup}
                  loading={backupLoading}
                  size="large"
                >
                  创建备份
                </Button>
              </Space>
            </Card>

            <Card title="数据恢复">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text>从备份文件恢复数据。恢复前会自动验证备份文件的完整性。</Text>
                  <br />
                  <Text type="warning">注意：恢复操作不会覆盖现有数据，只会添加新数据。</Text>
                </div>
                <Upload
                  accept=".zip"
                  beforeUpload={(file) => {
                    handleRestoreBackup(file);
                    return false;
                  }}
                  showUploadList={false}
                >
                  <Button
                    icon={<CloudUploadOutlined />}
                    loading={restoreLoading}
                    size="large"
                  >
                    选择备份文件恢复
                  </Button>
                </Upload>
              </Space>
            </Card>

            <Card title="导出数据">
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div>
                  <Text>选择导出格式：</Text>
                  <div style={{ marginTop: 16 }}>
                    <Space wrap>
                      <Button
                        icon={<ExportOutlined />}
                        onClick={() => handleExport('markdown')}
                      >
                        导出为 Markdown
                      </Button>
                      <Button
                        icon={<ExportOutlined />}
                        onClick={() => handleExport('json')}
                      >
                        导出为 JSON
                      </Button>
                      <Button
                        icon={<ExportOutlined />}
                        onClick={() => handleExport('html')}
                      >
                        导出为 HTML
                      </Button>
                    </Space>
                  </div>
                </div>

                <Divider />

                <div>
                  <Title level={5}>导入数据</Title>
                  <Text type="secondary">
                    从其他平台导入知识条目
                  </Text>
                  <div style={{ marginTop: 16 }}>
                    <Upload>
                      <Button icon={<UploadOutlined />}>
                        选择文件
                      </Button>
                    </Upload>
                    <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                      支持 Markdown、JSON 格式
                    </Text>
                  </div>
                </div>

                <Divider />

                <div>
                  <Title level={5}>外部平台导入</Title>
                  <Text type="secondary">
                    从 CSDN、微信公众号、Notion 等平台导入内容
                  </Text>
                  <div style={{ marginTop: 16 }}>
                    <Button icon={<ImportOutlined />} disabled>
                      配置导入源（开发中）
                    </Button>
                  </div>
                </div>
              </Space>
            </Card>
          </Space>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default SettingsPage;
