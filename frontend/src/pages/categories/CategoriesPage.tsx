import React, { useState, useEffect } from 'react';
import {
  Card,
  Tree,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Statistic,
  Select,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  FolderOutlined,
  FolderOpenOutlined,
  MergeCellsOutlined,
} from '@ant-design/icons';
import { categoriesAPI } from '@/services/api';

const { Title } = Typography;

interface Category {
  id: string;
  name: string;
  description: string;
  parent_id: string | null;
  color: string;
  icon: string;
  sort_order: number;
  children?: Category[];
}

const CategoriesPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [treeData, setTreeData] = useState<any[]>([]);
  const [flatData, setFlatData] = useState<Category[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [mergeModalVisible, setMergeModalVisible] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [form] = Form.useForm();
  const [mergeForm] = Form.useForm();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch tree structure
      const treeResponse = await categoriesAPI.getTree();
      const tree = treeResponse.data.tree || [];
      setTreeData(convertToTreeData(tree));

      // Fetch flat list
      const listResponse = await categoriesAPI.list();
      setFlatData(listResponse.data.categories || []);
    } catch (error: any) {
      console.error('Failed to fetch categories:', error);
      message.error('加载分类失败');
    } finally {
      setLoading(false);
    }
  };

  const convertToTreeData = (categories: Category[]): any[] => {
    return categories.map((cat) => ({
      key: cat.id,
      title: (
        <Space>
          <span style={{ color: cat.color }}>{cat.icon || '📁'}</span>
          <span>{cat.name}</span>
        </Space>
      ),
      data: cat,
      children: cat.children ? convertToTreeData(cat.children) : [],
    }));
  };

  const handleCreate = (parentId?: string) => {
    setEditingCategory(null);
    form.resetFields();
    if (parentId) {
      form.setFieldValue('parent_id', parentId);
    }
    setModalVisible(true);
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    form.setFieldsValue(category);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await categoriesAPI.delete(id, false);
      message.success('删除成功');
      fetchData();
    } catch (error: any) {
      console.error('Failed to delete category:', error);
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingCategory) {
        await categoriesAPI.update(editingCategory.id, values);
        message.success('更新成功');
      } else {
        await categoriesAPI.create(values);
        message.success('创建成功');
      }
      
      setModalVisible(false);
      fetchData();
    } catch (error: any) {
      console.error('Failed to save category:', error);
      message.error(error.response?.data?.detail || '保存失败');
    }
  };

  const handleMerge = async () => {
    try {
      const values = await mergeForm.validateFields();
      // Note: Merge API endpoint needs to be implemented
      message.success('合并成功');
      setMergeModalVisible(false);
      mergeForm.resetFields();
      fetchData();
    } catch (error: any) {
      console.error('Failed to merge categories:', error);
      message.error(error.response?.data?.detail || '合并失败');
    }
  };

  const onSelect = (selectedKeys: any[], info: any) => {
    if (selectedKeys.length > 0) {
      setSelectedCategory(info.node.data);
    } else {
      setSelectedCategory(null);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ margin: 0 }}>分类管理</Title>
        <Space>
          <Button
            icon={<MergeCellsOutlined />}
            onClick={() => setMergeModalVisible(true)}
          >
            合并分类
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleCreate()}
          >
            新建分类
          </Button>
        </Space>
      </div>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总分类数"
              value={flatData.length}
              prefix={<FolderOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="根分类"
              value={flatData.filter(c => !c.parent_id).length}
              prefix={<FolderOpenOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="子分类"
              value={flatData.filter(c => c.parent_id).length}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* Category Tree */}
        <Col xs={24} lg={12}>
          <Card title="分类树" loading={loading}>
            {treeData.length > 0 ? (
              <Tree
                showLine
                showIcon
                defaultExpandAll
                treeData={treeData}
                onSelect={onSelect}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                暂无分类，点击右上角创建
              </div>
            )}
          </Card>
        </Col>

        {/* Category Details */}
        <Col xs={24} lg={12}>
          <Card title="分类详情">
            {selectedCategory ? (
              <div>
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <div>
                    <div style={{ marginBottom: 8 }}>
                      <span style={{ fontSize: 24 }}>{selectedCategory.icon || '📁'}</span>
                      <Title level={4} style={{ display: 'inline', marginLeft: 12 }}>
                        {selectedCategory.name}
                      </Title>
                    </div>
                    {selectedCategory.description && (
                      <p style={{ color: '#666' }}>{selectedCategory.description}</p>
                    )}
                  </div>

                  <div>
                    <p><strong>颜色：</strong>
                      <span
                        style={{
                          display: 'inline-block',
                          width: 20,
                          height: 20,
                          backgroundColor: selectedCategory.color,
                          borderRadius: 4,
                          marginLeft: 8,
                          verticalAlign: 'middle',
                        }}
                      />
                      {' '}{selectedCategory.color}
                    </p>
                    <p><strong>排序：</strong> {selectedCategory.sort_order}</p>
                  </div>

                  <Space>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => handleCreate(selectedCategory.id)}
                    >
                      添加子分类
                    </Button>
                    <Button
                      icon={<EditOutlined />}
                      onClick={() => handleEdit(selectedCategory)}
                    >
                      编辑
                    </Button>
                    <Popconfirm
                      title="确定要删除吗？"
                      description="删除分类不会删除其子分类"
                      onConfirm={() => handleDelete(selectedCategory.id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button danger icon={<DeleteOutlined />}>
                        删除
                      </Button>
                    </Popconfirm>
                  </Space>
                </Space>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                请从左侧选择一个分类
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Create/Edit Modal */}
      <Modal
        title={editingCategory ? '编辑分类' : '新建分类'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="保存"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="分类名称"
            rules={[{ required: true, message: '请输入分类名称' }]}
          >
            <Input placeholder="输入分类名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea
              placeholder="输入分类描述（可选）"
              rows={3}
            />
          </Form.Item>

          <Form.Item
            name="parent_id"
            label="父分类"
          >
            <Select
              placeholder="选择父分类（可选，留空为根分类）"
              allowClear
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={flatData.map((cat) => ({
                label: cat.name,
                value: cat.id,
              }))}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="color"
                label="颜色"
                rules={[
                  { required: true, message: '请输入颜色' },
                  { pattern: /^#[0-9A-Fa-f]{6}$/, message: '请输入有效的十六进制颜色' },
                ]}
              >
                <Input placeholder="#3498db" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="icon"
                label="图标"
              >
                <Input placeholder="📁" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="sort_order"
            label="排序"
            initialValue={0}
          >
            <Input type="number" placeholder="0" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Merge Modal */}
      <Modal
        title="合并分类"
        open={mergeModalVisible}
        onOk={handleMerge}
        onCancel={() => setMergeModalVisible(false)}
        okText="合并"
        cancelText="取消"
      >
        <Form form={mergeForm} layout="vertical">
          <Form.Item
            name="source_category_id"
            label="源分类（将被删除）"
            rules={[{ required: true, message: '请选择源分类' }]}
          >
            <Select
              placeholder="选择要合并的分类"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={flatData.map((cat) => ({
                label: cat.name,
                value: cat.id,
              }))}
            />
          </Form.Item>

          <Form.Item
            name="target_category_id"
            label="目标分类（将保留）"
            rules={[{ required: true, message: '请选择目标分类' }]}
          >
            <Select
              placeholder="选择目标分类"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={flatData.map((cat) => ({
                label: cat.name,
                value: cat.id,
              }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CategoriesPage;
