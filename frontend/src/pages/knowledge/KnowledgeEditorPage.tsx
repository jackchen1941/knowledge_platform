import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Button,
  Select,
  Card,
  Space,
  message,
  Switch,
  Spin,
} from 'antd';
import { SaveOutlined, ArrowLeftOutlined, EyeOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { knowledgeAPI, categoriesAPI, tagsAPI } from '@/services/api';
import { formatErrorMessage } from '@/utils/errorHandler';

const { TextArea } = Input;

interface FormValues {
  title: string;
  content: string;
  summary?: string;
  category_id?: string;
  tag_ids?: string[];
  is_published: boolean;
  visibility: string;
}

const KnowledgeEditorPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [tagSearchText, setTagSearchText] = useState('');

  const isEditMode = !!id;

  useEffect(() => {
    fetchCategories();
    fetchTags();
    if (isEditMode) {
      fetchData();
    }
  }, [id]);

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.list();
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchTags = async (search?: string) => {
    try {
      const response = await tagsAPI.list({ search });
      setTags(response.data.tags || []);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await knowledgeAPI.get(id!);
      const data = response.data;
      form.setFieldsValue({
        title: data.title,
        content: data.content,
        summary: data.summary,
        category_id: data.category?.id,
        tag_ids: data.tags.map((t: any) => t.id),
        is_published: data.is_published,
        visibility: data.visibility,
      });
    } catch (error: any) {
      console.error('Failed to fetch knowledge item:', error);
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: FormValues) => {
    setSaving(true);
    try {
      const data = {
        ...values,
        content_type: 'markdown',
      };

      if (isEditMode) {
        await knowledgeAPI.update(id!, data);
        message.success('保存成功');
      } else {
        const response = await knowledgeAPI.create(data);
        message.success('创建成功');
        navigate(`/knowledge/${response.data.id}`);
      }
    } catch (error: any) {
      console.error('Failed to save:', error);
      message.error(formatErrorMessage(error, '保存失败'));
    } finally {
      setSaving(false);
    }
  };

  const handleTagSearch = (value: string) => {
    setTagSearchText(value);
    if (value) {
      fetchTags(value);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(isEditMode ? `/knowledge/${id}` : '/knowledge')}
          style={{ marginBottom: 16 }}
        >
          返回
        </Button>
        <h2>{isEditMode ? '编辑知识' : '新建知识'}</h2>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          is_published: false,
          visibility: 'private',
        }}
      >
        <Card style={{ marginBottom: 16 }}>
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="输入知识标题" size="large" />
          </Form.Item>

          <Form.Item
            name="summary"
            label="摘要"
          >
            <TextArea
              placeholder="简要描述这篇知识的内容（可选）"
              rows={2}
            />
          </Form.Item>

          <Space size="large" style={{ width: '100%' }}>
            <Form.Item
              name="category_id"
              label="分类"
              style={{ flex: 1, minWidth: 200 }}
            >
              <Select
                placeholder="选择分类"
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                options={categories.map((cat) => ({
                  label: cat.name,
                  value: cat.id,
                }))}
              />
            </Form.Item>

            <Form.Item
              name="tag_ids"
              label="标签"
              style={{ flex: 1, minWidth: 200 }}
            >
              <Select
                mode="multiple"
                placeholder="选择或搜索标签"
                allowClear
                showSearch
                onSearch={handleTagSearch}
                filterOption={false}
                options={tags.map((tag) => ({
                  label: tag.name,
                  value: tag.id,
                }))}
              />
            </Form.Item>
          </Space>

          <Space size="large">
            <Form.Item
              name="visibility"
              label="可见性"
            >
              <Select style={{ width: 120 }}>
                <Select.Option value="private">私有</Select.Option>
                <Select.Option value="shared">共享</Select.Option>
                <Select.Option value="public">公开</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="is_published"
              label="发布状态"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="已发布"
                unCheckedChildren="草稿"
              />
            </Form.Item>
          </Space>
        </Card>

        <Card title="内容" style={{ marginBottom: 16 }}>
          <Form.Item
            name="content"
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <TextArea
              placeholder="使用 Markdown 格式编写内容..."
              rows={20}
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>
        </Card>

        <Card>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={saving}
              size="large"
            >
              保存
            </Button>
            <Button
              size="large"
              onClick={() => navigate(isEditMode ? `/knowledge/${id}` : '/knowledge')}
            >
              取消
            </Button>
            {isEditMode && (
              <Button
                icon={<EyeOutlined />}
                size="large"
                onClick={() => navigate(`/knowledge/${id}`)}
              >
                预览
              </Button>
            )}
          </Space>
        </Card>
      </Form>
    </div>
  );
};

export default KnowledgeEditorPage;
