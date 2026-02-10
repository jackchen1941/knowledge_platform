import React, { useState } from 'react';
import {
  Input,
  Card,
  List,
  Tag,
  Typography,
  Space,
  Button,
  Row,
  Col,
  Select,
  DatePicker,
  InputNumber,
  Collapse,
  Empty,
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { searchAPI, categoriesAPI, tagsAPI } from '@/services/api';
import dayjs from 'dayjs';

const { Search } = Input;
const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Panel } = Collapse;

interface SearchResult {
  id: string;
  title: string;
  summary: string;
  content_type: string;
  word_count: number;
  view_count: number;
  created_at: string;
  updated_at: string;
  category: { id: string; name: string } | null;
  tags: Array<{ id: string; name: string; color: string }>;
}

const SearchPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  
  // Advanced filters
  const [categoryId, setCategoryId] = useState<string | undefined>();
  const [tagIds, setTagIds] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [minWords, setMinWords] = useState<number | undefined>();
  const [maxWords, setMaxWords] = useState<number | undefined>();
  const [visibility, setVisibility] = useState<string | undefined>();
  const [isPublished, setIsPublished] = useState<boolean | undefined>();
  
  const [categories, setCategories] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);

  React.useEffect(() => {
    fetchCategories();
    fetchTags();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.list();
      setCategories(response.data.categories || []);
    } catch (error) {
      console.warn('Categories API not available, using empty list');
      setCategories([]);
    }
  };

  const fetchTags = async () => {
    try {
      const response = await tagsAPI.list();
      setTags(response.data.tags || []);
    } catch (error) {
      console.warn('Tags API not available, using empty list');
      setTags([]);
    }
  };

  const handleSearch = async (value?: string) => {
    const query = value !== undefined ? value : searchText;
    if (!query && !categoryId && tagIds.length === 0) {
      return;
    }

    setLoading(true);
    try {
      const params: any = {
        q: query,
        page,
        page_size: pageSize,
        sort_by: 'updated_at',
        sort_order: 'desc',
      };

      if (categoryId) params.category_id = categoryId;
      if (tagIds.length > 0) params.tag_ids = tagIds;
      if (visibility) params.visibility = visibility;
      if (isPublished !== undefined) params.is_published = isPublished;
      if (minWords) params.min_word_count = minWords;
      if (maxWords) params.max_word_count = maxWords;
      
      if (dateRange) {
        params.created_after = dateRange[0].toISOString();
        params.created_before = dateRange[1].toISOString();
      }

      const response = await searchAPI.search(params);
      setResults(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch (error: any) {
      console.warn('Search API not available, showing empty results');
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestions = async (value: string) => {
    if (value.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await searchAPI.suggestions(value);
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.warn('Suggestions API not available, using empty list');
      setSuggestions([]);
    }
  };

  const clearFilters = () => {
    setCategoryId(undefined);
    setTagIds([]);
    setDateRange(null);
    setMinWords(undefined);
    setMaxWords(undefined);
    setVisibility(undefined);
    setIsPublished(undefined);
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        搜索知识
      </Title>

      {/* Search Bar */}
      <Card style={{ marginBottom: 16 }}>
        <Search
          placeholder="搜索标题、内容或摘要..."
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          value={searchText}
          onChange={(e) => {
            setSearchText(e.target.value);
            handleSuggestions(e.target.value);
          }}
          onSearch={handleSearch}
          loading={loading}
        />
        
        {/* Search Suggestions */}
        {suggestions.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <Text type="secondary">建议：</Text>
            <Space wrap style={{ marginTop: 4 }}>
              {suggestions.slice(0, 5).map((item, index) => (
                <Tag
                  key={index}
                  style={{ cursor: 'pointer' }}
                  onClick={() => {
                    setSearchText(item.text);
                    setSuggestions([]);
                    handleSearch(item.text);
                  }}
                >
                  {item.text}
                </Tag>
              ))}
            </Space>
          </div>
        )}
      </Card>

      {/* Advanced Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Collapse
          ghost
          items={[
            {
              key: '1',
              label: (
                <Space>
                  <FilterOutlined />
                  <Text strong>高级筛选</Text>
                </Space>
              ),
              children: (
                <div>
                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12} lg={6}>
                      <Text>分类</Text>
                      <Select
                        placeholder="选择分类"
                        allowClear
                        style={{ width: '100%', marginTop: 8 }}
                        value={categoryId}
                        onChange={setCategoryId}
                        options={categories.map((cat) => ({
                          label: cat.name,
                          value: cat.id,
                        }))}
                      />
                    </Col>

                    <Col xs={24} sm={12} lg={6}>
                      <Text>标签</Text>
                      <Select
                        mode="multiple"
                        placeholder="选择标签"
                        allowClear
                        style={{ width: '100%', marginTop: 8 }}
                        value={tagIds}
                        onChange={setTagIds}
                        options={tags.map((tag) => ({
                          label: tag.name,
                          value: tag.id,
                        }))}
                      />
                    </Col>

                    <Col xs={24} sm={12} lg={6}>
                      <Text>状态</Text>
                      <Select
                        placeholder="选择状态"
                        allowClear
                        style={{ width: '100%', marginTop: 8 }}
                        value={isPublished}
                        onChange={setIsPublished}
                        options={[
                          { label: '已发布', value: true },
                          { label: '草稿', value: false },
                        ]}
                      />
                    </Col>

                    <Col xs={24} sm={12} lg={6}>
                      <Text>可见性</Text>
                      <Select
                        placeholder="选择可见性"
                        allowClear
                        style={{ width: '100%', marginTop: 8 }}
                        value={visibility}
                        onChange={setVisibility}
                        options={[
                          { label: '私有', value: 'private' },
                          { label: '共享', value: 'shared' },
                          { label: '公开', value: 'public' },
                        ]}
                      />
                    </Col>

                    <Col xs={24} sm={12} lg={8}>
                      <Text>创建日期范围</Text>
                      <RangePicker
                        style={{ width: '100%', marginTop: 8 }}
                        value={dateRange}
                        onChange={(dates) => setDateRange(dates as any)}
                      />
                    </Col>

                    <Col xs={24} sm={12} lg={8}>
                      <Text>最小字数</Text>
                      <InputNumber
                        placeholder="最小字数"
                        style={{ width: '100%', marginTop: 8 }}
                        value={minWords}
                        onChange={(value) => setMinWords(value || undefined)}
                        min={0}
                      />
                    </Col>

                    <Col xs={24} sm={12} lg={8}>
                      <Text>最大字数</Text>
                      <InputNumber
                        placeholder="最大字数"
                        style={{ width: '100%', marginTop: 8 }}
                        value={maxWords}
                        onChange={(value) => setMaxWords(value || undefined)}
                        min={0}
                      />
                    </Col>
                  </Row>

                  <div style={{ marginTop: 16, textAlign: 'right' }}>
                    <Space>
                      <Button onClick={clearFilters}>清除筛选</Button>
                      <Button type="primary" onClick={() => handleSearch()}>
                        应用筛选
                      </Button>
                    </Space>
                  </div>
                </div>
              ),
            },
          ]}
        />
      </Card>

      {/* Search Results */}
      <Card
        title={
          total > 0 ? (
            <Text>找到 {total} 条结果</Text>
          ) : (
            <Text>搜索结果</Text>
          )
        }
      >
        {results.length > 0 ? (
          <List
            dataSource={results}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              onChange: (page) => {
                setPage(page);
                handleSearch();
              },
              showTotal: (total) => `共 ${total} 条`,
            }}
            renderItem={(item) => (
              <List.Item
                key={item.id}
                actions={[
                  <Button
                    type="link"
                    onClick={() => navigate(`/knowledge/${item.id}`)}
                  >
                    查看详情
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  avatar={<FileTextOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                  title={
                    <a onClick={() => navigate(`/knowledge/${item.id}`)}>
                      {item.title}
                    </a>
                  }
                  description={
                    <div>
                      <Text type="secondary" ellipsis>
                        {item.summary || '暂无摘要'}
                      </Text>
                      <div style={{ marginTop: 8 }}>
                        <Space size="small" wrap>
                          {item.category && (
                            <Tag color="blue">{item.category.name}</Tag>
                          )}
                          {item.tags.slice(0, 3).map((tag) => (
                            <Tag key={tag.id} color={tag.color}>
                              {tag.name}
                            </Tag>
                          ))}
                          <Text type="secondary">
                            <ClockCircleOutlined /> {item.word_count} 字
                          </Text>
                          <Text type="secondary">
                            {new Date(item.updated_at).toLocaleDateString('zh-CN')}
                          </Text>
                        </Space>
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty description="暂无搜索结果" />
        )}
      </Card>
    </div>
  );
};

export default SearchPage;
