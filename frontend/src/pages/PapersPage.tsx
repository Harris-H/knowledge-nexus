import { useEffect, useState } from "react";
import {
  Table,
  Tag,
  Space,
  Input,
  Button,
  Tooltip,
  Card,
  Drawer,
  Descriptions,
  Empty,
  Popconfirm,
  message,
} from "antd";
import {
  SearchOutlined,
  EyeOutlined,
  NodeIndexOutlined,
  LinkOutlined,
  DeleteOutlined,
  FilePdfOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { useStore } from "../stores";
import { papersApi } from "../api";
import type { Paper } from "../api";

export default function PapersPage() {
  const {
    papers,
    papersTotal,
    papersLoading,
    fetchPapers,
    fetchSubgraph,
    setPaperSort,
  } = useStore();
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [detailPaper, setDetailPaper] = useState<Paper | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [batchDeleting, setBatchDeleting] = useState(false);

  const handleDelete = async (id: string) => {
    try {
      await papersApi.delete(id);
      message.success("论文已删除");
      if (detailPaper?.id === id) setDetailPaper(null);
      setSelectedIds((prev) => prev.filter((x) => x !== id));
      fetchPapers(page, 20);
    } catch {
      message.error("删除失败");
    }
  };

  const handleBatchDelete = async () => {
    if (selectedIds.length === 0) return;
    setBatchDeleting(true);
    try {
      const { data } = await papersApi.batchDelete(selectedIds);
      message.success(`已删除 ${data.deleted} 篇论文`);
      setSelectedIds([]);
      if (detailPaper && selectedIds.includes(detailPaper.id))
        setDetailPaper(null);
      fetchPapers(page, 20);
    } catch {
      message.error("批量删除失败");
    } finally {
      setBatchDeleting(false);
    }
  };

  const paperSort = useStore((s) => s.paperSort);

  useEffect(() => {
    fetchPapers(page, 20);
  }, [page, paperSort, fetchPapers]);

  const columns: ColumnsType<Paper> = [
    {
      title: "评分",
      dataIndex: "impact_score",
      width: 70,
      sorter: true,
      render: (score: number) => (
        <Tag color={score >= 80 ? "red" : score >= 50 ? "orange" : "blue"}>
          {score.toFixed(1)}
        </Tag>
      ),
    },
    {
      title: "论文标题",
      dataIndex: "title",
      ellipsis: true,
      render: (_title: string, record) => (
        <Tooltip title={record.summary || record.title}>
          <a onClick={() => setDetailPaper(record)}>
            {record.key_contributions ? (
              <>
                <strong>{record.key_contributions}</strong>
                <span style={{ color: "#999", fontSize: 12, marginLeft: 6 }}>
                  {record.title.length > 40
                    ? record.title.slice(0, 38) + "..."
                    : record.title}
                </span>
              </>
            ) : (
              record.title
            )}
          </a>
        </Tooltip>
      ),
    },
    {
      title: "年份",
      dataIndex: "year",
      width: 70,
      sorter: true,
    },
    {
      title: "引用",
      dataIndex: "citation_count",
      width: 80,
      sorter: true,
      defaultSortOrder: "descend" as const,
      render: (v: number) => v?.toLocaleString(),
    },
    {
      title: "领域",
      dataIndex: "fields_of_study",
      width: 150,
      ellipsis: true,
      render: (v: string) =>
        v ? (
          <Space size={2} wrap>
            {v.split(", ").slice(0, 2).map((f) => (
              <Tag key={f} color="cyan" style={{ fontSize: 11 }}>
                {f}
              </Tag>
            ))}
          </Space>
        ) : (
          "-"
        ),
    },
    {
      title: "会议/期刊",
      dataIndex: "venue",
      width: 120,
      ellipsis: true,
    },
    {
      title: "入库时间",
      dataIndex: "created_at",
      width: 160,
      sorter: true,
      render: (v: string) =>
        v
          ? new Date(v).toLocaleString("zh-CN", {
              year: "numeric",
              month: "2-digit",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
              timeZone: "Asia/Shanghai",
            })
          : "-",
    },
    {
      title: "操作",
      width: 170,
      render: (_: unknown, record: Paper) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => setDetailPaper(record)}
            />
          </Tooltip>
          <Tooltip title="在图谱中查看">
            <Button
              size="small"
              icon={<NodeIndexOutlined />}
              onClick={() => fetchSubgraph(record.id)}
            />
          </Tooltip>
          {record.pdf_path && (
            <Tooltip title="下载 PDF">
              <Button
                size="small"
                icon={<FilePdfOutlined />}
                style={{ color: "#cf1322" }}
                href={`${import.meta.env.VITE_API_BASE || "/api/v1"}/papers/${record.id}/pdf`}
                target="_blank"
              />
            </Tooltip>
          )}
          {record.url && (
            <Tooltip title="原文链接">
              <Button
                size="small"
                icon={<LinkOutlined />}
                href={record.url}
                target="_blank"
              />
            </Tooltip>
          )}
          <Popconfirm
            title="确定删除这篇论文？"
            description="关联的关系也会一并删除"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      <Card
        title={`论文库 (${papersTotal} 篇)`}
        extra={
          <Space>
            {selectedIds.length > 0 && (
              <Popconfirm
                title={`确定删除选中的 ${selectedIds.length} 篇论文？`}
                description="关联的关系也会一并删除，此操作不可撤销"
                onConfirm={handleBatchDelete}
                okText="删除"
                cancelText="取消"
                okButtonProps={{ danger: true }}
              >
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  loading={batchDeleting}
                >
                  批量删除 ({selectedIds.length})
                </Button>
              </Popconfirm>
            )}
            <Input.Search
              placeholder="搜索论文..."
              prefix={<SearchOutlined />}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={() => fetchPapers(1)}
              style={{ width: 300 }}
              allowClear
            />
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={papers}
          rowKey="id"
          rowSelection={{
            selectedRowKeys: selectedIds,
            onChange: (keys) => setSelectedIds(keys as string[]),
          }}
          loading={papersLoading}
          size="small"
          pagination={{
            current: page,
            total: papersTotal,
            pageSize: 20,
            showTotal: (t) => `共 ${t} 篇`,
          }}
          onChange={(pag, _filters, sorter) => {
            const newPage = pag.current ?? 1;
            const s = Array.isArray(sorter) ? sorter[0] : sorter;
            if (s?.field && s?.order) {
              const field = String(s.field);
              const order = s.order === "ascend" ? "asc" : "desc";
              setPaperSort(field, order);
            }
            setPage(newPage);
          }}
          locale={{ emptyText: <Empty description="暂无论文，请先启动爬取任务" /> }}
        />
      </Card>

      <Drawer
        title="论文详情"
        open={!!detailPaper}
        onClose={() => setDetailPaper(null)}
        width={600}
      >
        {detailPaper && (
          <Descriptions column={1} bordered size="small">
            {detailPaper.key_contributions && (
              <Descriptions.Item label="核心工作">
                <strong style={{ fontSize: 16 }}>
                  {detailPaper.key_contributions}
                </strong>
              </Descriptions.Item>
            )}
            {detailPaper.summary && (
              <Descriptions.Item label="一句话简介">
                <span style={{ fontSize: 14, color: "#333", lineHeight: 1.6 }}>
                  💡 {detailPaper.summary}
                </span>
              </Descriptions.Item>
            )}
            <Descriptions.Item label="论文标题">
              {detailPaper.title}
            </Descriptions.Item>
            <Descriptions.Item label="作者">
              {detailPaper.authors?.join(", ") || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="年份">
              {detailPaper.year || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="会议/期刊">
              {detailPaper.venue || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="所属领域">
              {detailPaper.fields_of_study ? (
                <Space size={4} wrap>
                  {detailPaper.fields_of_study.split(", ").map((f) => (
                    <Tag key={f} color="cyan">
                      {f}
                    </Tag>
                  ))}
                </Space>
              ) : (
                "-"
              )}
            </Descriptions.Item>
            <Descriptions.Item label="引用量">
              {detailPaper.citation_count?.toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="影响力评分">
              <Tag
                color={
                  detailPaper.impact_score >= 80
                    ? "red"
                    : detailPaper.impact_score >= 50
                    ? "orange"
                    : "blue"
                }
              >
                {detailPaper.impact_score.toFixed(1)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="DOI">
              {detailPaper.doi ? (
                <a
                  href={`https://doi.org/${detailPaper.doi}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {detailPaper.doi}
                </a>
              ) : (
                "-"
              )}
            </Descriptions.Item>
            <Descriptions.Item label="arXiv">
              {detailPaper.arxiv_id ? (
                <a
                  href={`https://arxiv.org/abs/${detailPaper.arxiv_id}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {detailPaper.arxiv_id}
                </a>
              ) : (
                "-"
              )}
            </Descriptions.Item>
            <Descriptions.Item label="摘要">
              <div style={{ maxHeight: 200, overflow: "auto", fontSize: 13 }}>
                {detailPaper.abstract || "暂无摘要"}
              </div>
            </Descriptions.Item>
            {detailPaper.pdf_path && (
              <Descriptions.Item label="PDF">
                <Button
                  type="link"
                  icon={<FilePdfOutlined />}
                  href={`${import.meta.env.VITE_API_BASE || "/api/v1"}/papers/${detailPaper.id}/pdf`}
                  target="_blank"
                  style={{ padding: 0 }}
                >
                  下载 PDF
                </Button>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Drawer>
    </div>
  );
}
