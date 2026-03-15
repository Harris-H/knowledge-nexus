import { useEffect, useState, useCallback } from "react";
import {
  Table, Tag, Button, Space, message, Popconfirm, Drawer, Typography, Input, Select,
} from "antd";
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { knowledgeNodesApi } from "../api";
import type { KnowledgeNode } from "../api";

const { Text, Paragraph } = Typography;
const { Search } = Input;

const NODE_TYPE_OPTIONS = [
  { value: "phenomenon", label: "🌿 现象" },
  { value: "theorem", label: "📐 定理" },
  { value: "law", label: "⚖️ 定律" },
  { value: "method", label: "🔧 方法" },
  { value: "concept", label: "💡 概念" },
  { value: "principle", label: "🎯 原理" },
  { value: "process", label: "🔄 过程" },
  { value: "structure", label: "🏗️ 结构" },
];

const DOMAIN_OPTIONS = [
  { value: "biology", label: "🧬 生物学" },
  { value: "physics", label: "⚛️ 物理学" },
  { value: "mathematics", label: "📊 数学" },
  { value: "computer_science", label: "💻 计算机科学" },
  { value: "chemistry", label: "🧪 化学" },
  { value: "neuroscience", label: "🧠 神经科学" },
  { value: "engineering", label: "⚙️ 工程学" },
  { value: "economics", label: "📈 经济学" },
  { value: "philosophy", label: "🤔 哲学" },
  { value: "ecology", label: "🌍 生态学" },
];

const NODE_TYPE_COLORS: Record<string, string> = {
  phenomenon: "green",
  theorem: "gold",
  law: "red",
  method: "purple",
  concept: "cyan",
  principle: "magenta",
  process: "orange",
  structure: "blue",
};

const DOMAIN_COLORS: Record<string, string> = {
  biology: "green",
  physics: "blue",
  mathematics: "gold",
  computer_science: "purple",
  chemistry: "orange",
  neuroscience: "magenta",
  engineering: "geekblue",
  economics: "lime",
  philosophy: "cyan",
  ecology: "green",
};

export default function KnowledgeNodesPage() {
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [detailNode, setDetailNode] = useState<KnowledgeNode | null>(null);
  const [filterDomain, setFilterDomain] = useState<string | undefined>();
  const [filterType, setFilterType] = useState<string | undefined>();

  const fetchNodes = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = { size: 100 };
      if (filterDomain) params.domain = filterDomain;
      if (filterType) params.node_type = filterType;
      const res = await knowledgeNodesApi.list(params);
      setNodes(res.data.items);
      setTotal(res.data.total);
    } catch {
      message.error("加载知识节点失败");
    } finally {
      setLoading(false);
    }
  }, [filterDomain, filterType]);

  useEffect(() => {
    fetchNodes();
  }, [fetchNodes]);

  const handleDelete = async (id: string) => {
    await knowledgeNodesApi.delete(id);
    message.success("已删除");
    fetchNodes();
  };

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) return;
    await knowledgeNodesApi.batchDelete(selectedRowKeys);
    message.success(`已删除 ${selectedRowKeys.length} 个节点`);
    setSelectedRowKeys([]);
    fetchNodes();
  };

  const columns: ColumnsType<KnowledgeNode> = [
    {
      title: "名称",
      dataIndex: "name",
      key: "name",
      width: 200,
      render: (name: string, record) => (
        <a onClick={() => setDetailNode(record)}>{name}</a>
      ),
    },
    {
      title: "类型",
      dataIndex: "node_type",
      key: "node_type",
      width: 100,
      render: (t: string) => (
        <Tag color={NODE_TYPE_COLORS[t] || "default"}>
          {NODE_TYPE_OPTIONS.find((o) => o.value === t)?.label || t}
        </Tag>
      ),
    },
    {
      title: "领域",
      dataIndex: "domain",
      key: "domain",
      width: 120,
      render: (d: string) => (
        <Tag color={DOMAIN_COLORS[d] || "default"}>
          {DOMAIN_OPTIONS.find((o) => o.value === d)?.label || d}
        </Tag>
      ),
    },
    {
      title: "简介",
      dataIndex: "summary",
      key: "summary",
      ellipsis: true,
      render: (s: string) => <Text type="secondary">{s || "—"}</Text>,
    },
    {
      title: "年份",
      dataIndex: "year",
      key: "year",
      width: 80,
      render: (y: number) => y || "—",
    },
    {
      title: "操作",
      key: "action",
      width: 80,
      render: (_, record) => (
        <Popconfirm
          title="确认删除？"
          description="将同时删除该节点的所有关联关系"
          onConfirm={() => handleDelete(record.id)}
        >
          <Button type="text" danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      {/* 工具栏 */}
      <Space style={{ marginBottom: 12 }} wrap>
        <Select
          placeholder="按领域筛选"
          allowClear
          style={{ width: 160 }}
          options={DOMAIN_OPTIONS}
          value={filterDomain}
          onChange={setFilterDomain}
        />
        <Select
          placeholder="按类型筛选"
          allowClear
          style={{ width: 140 }}
          options={NODE_TYPE_OPTIONS}
          value={filterType}
          onChange={setFilterType}
        />
        <Text type="secondary">
          共 {total} 个知识节点
        </Text>
        {selectedRowKeys.length > 0 && (
          <Popconfirm
            title={`确认删除 ${selectedRowKeys.length} 个节点？`}
            onConfirm={handleBatchDelete}
          >
            <Button danger size="small" icon={<DeleteOutlined />}>
              批量删除 ({selectedRowKeys.length})
            </Button>
          </Popconfirm>
        )}
      </Space>

      {/* 表格 */}
      <Table
        dataSource={nodes}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="small"
        pagination={{ pageSize: 50, showSizeChanger: false }}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys as string[]),
        }}
      />

      {/* 详情抽屉 */}
      <Drawer
        title={detailNode?.name}
        open={!!detailNode}
        onClose={() => setDetailNode(null)}
        width={480}
      >
        {detailNode && (
          <div>
            <Space wrap style={{ marginBottom: 16 }}>
              <Tag color={NODE_TYPE_COLORS[detailNode.node_type] || "default"}>
                {NODE_TYPE_OPTIONS.find((o) => o.value === detailNode.node_type)?.label || detailNode.node_type}
              </Tag>
              <Tag color={DOMAIN_COLORS[detailNode.domain] || "default"}>
                {DOMAIN_OPTIONS.find((o) => o.value === detailNode.domain)?.label || detailNode.domain}
              </Tag>
              {detailNode.year && <Tag>{detailNode.year}</Tag>}
            </Space>

            {detailNode.summary && (
              <>
                <Text strong>一句话简介</Text>
                <Paragraph style={{ marginTop: 4 }}>{detailNode.summary}</Paragraph>
              </>
            )}

            {detailNode.description && (
              <>
                <Text strong>详细描述</Text>
                <Paragraph style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>
                  {detailNode.description}
                </Paragraph>
              </>
            )}

            {detailNode.source_info && (
              <>
                <Text strong>来源</Text>
                <Paragraph style={{ marginTop: 4 }}>{detailNode.source_info}</Paragraph>
              </>
            )}

            {detailNode.tags && (
              <>
                <Text strong>标签</Text>
                <div style={{ marginTop: 4 }}>
                  {detailNode.tags.split(",").map((tag) => (
                    <Tag key={tag.trim()} style={{ marginBottom: 4 }}>
                      {tag.trim()}
                    </Tag>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
}
