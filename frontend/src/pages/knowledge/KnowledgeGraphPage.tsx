import React, { useEffect, useRef, useState } from 'react';
import { Card, Spin, message, Button, Select, Slider, Space, Drawer, List, Tag } from 'antd';
import { FullscreenOutlined, ReloadOutlined, ZoomInOutlined, ZoomOutOutlined } from '@ant-design/icons';
import * as d3 from 'd3';
import api from '../../services/api';

interface Node {
  id: string;
  title: string;
  is_published: boolean;
  word_count: number;
  category: string | null;
  tags: Array<{ name: string; color: string }>;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  type: string;
  description: string | null;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
  center_id?: string;
  depth?: number;
}

const KnowledgeGraphPage: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [loading, setLoading] = useState(false);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [depth, setDepth] = useState(2);
  const [centerId, setCenterId] = useState<string | undefined>(undefined);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadGraphData();
    loadStats();
  }, []);

  const loadGraphData = async (center?: string, d?: number) => {
    setLoading(true);
    try {
      const params: any = {};
      if (center) params.center_id = center;
      if (d !== undefined) params.depth = d;

      const response = await api.get('/graph', { params });
      setGraphData(response.data);
      renderGraph(response.data);
    } catch (error) {
      message.error('加载知识图谱失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/graph/stats');
      setStats(response.data);
    } catch (error) {
      console.error('加载统计失败', error);
    }
  };

  const renderGraph = (data: GraphData) => {
    if (!svgRef.current || !data.nodes.length) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create container for zoom
    const g = svg.append('g');

    // Setup zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes as any)
      .force('link', d3.forceLink(data.edges)
        .id((d: any) => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    // Create edges
    const link = g.append('g')
      .selectAll('line')
      .data(data.edges)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Create nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter()
      .append('circle')
      .attr('r', (d: any) => Math.min(10 + Math.sqrt(d.word_count) / 10, 30))
      .attr('fill', (d: any) => d.is_published ? '#1890ff' : '#d9d9d9')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (event, d: any) => {
        setSelectedNode(d);
        setDrawerVisible(true);
      })
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any);

    // Add labels
    const label = g.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter()
      .append('text')
      .text((d: any) => d.title.length > 15 ? d.title.substring(0, 15) + '...' : d.title)
      .attr('font-size', 12)
      .attr('dx', 15)
      .attr('dy', 4)
      .style('pointer-events', 'none');

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  };

  const handleReload = () => {
    loadGraphData(centerId, depth);
  };

  const handleDepthChange = (value: number) => {
    setDepth(value);
    if (centerId) {
      loadGraphData(centerId, value);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="知识图谱"
        extra={
          <Space>
            {stats && (
              <span style={{ marginRight: 16, fontSize: 14 }}>
                节点: {stats.total_items} | 链接: {stats.total_links} | 孤立: {stats.isolated_items}
              </span>
            )}
            {centerId && (
              <>
                <span>深度:</span>
                <Slider
                  min={1}
                  max={5}
                  value={depth}
                  onChange={handleDepthChange}
                  style={{ width: 100, marginLeft: 8, marginRight: 16 }}
                />
              </>
            )}
            <Button icon={<ReloadOutlined />} onClick={handleReload}>
              刷新
            </Button>
          </Space>
        }
      >
        <Spin spinning={loading}>
          <div style={{ position: 'relative', height: '70vh', border: '1px solid #d9d9d9', borderRadius: 4 }}>
            <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
            {!graphData?.nodes.length && !loading && (
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
                color: '#999'
              }}>
                <p>暂无知识图谱数据</p>
                <p style={{ fontSize: 12 }}>创建知识条目并建立关联后，图谱将在此显示</p>
              </div>
            )}
          </div>
        </Spin>
      </Card>

      <Drawer
        title="节点详情"
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={400}
      >
        {selectedNode && (
          <div>
            <h3>{selectedNode.title}</h3>
            <p>
              <strong>状态:</strong>{' '}
              <Tag color={selectedNode.is_published ? 'green' : 'default'}>
                {selectedNode.is_published ? '已发布' : '草稿'}
              </Tag>
            </p>
            <p><strong>字数:</strong> {selectedNode.word_count}</p>
            {selectedNode.category && (
              <p><strong>分类:</strong> {selectedNode.category}</p>
            )}
            {selectedNode.tags.length > 0 && (
              <div>
                <strong>标签:</strong>
                <div style={{ marginTop: 8 }}>
                  {selectedNode.tags.map((tag, index) => (
                    <Tag key={index} color={tag.color}>
                      {tag.name}
                    </Tag>
                  ))}
                </div>
              </div>
            )}
            <div style={{ marginTop: 24 }}>
              <Button
                type="primary"
                block
                onClick={() => {
                  setCenterId(selectedNode.id);
                  loadGraphData(selectedNode.id, depth);
                  setDrawerVisible(false);
                }}
              >
                以此为中心展示
              </Button>
              <Button
                block
                style={{ marginTop: 8 }}
                onClick={() => {
                  window.location.href = `/knowledge/${selectedNode.id}`;
                }}
              >
                查看详情
              </Button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default KnowledgeGraphPage;
