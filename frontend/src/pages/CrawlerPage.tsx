import { useEffect, useState } from "react";
import {
  Card,
  Button,
  Form,
  InputNumber,
  Select,
  Table,
  Tag,
  Progress,
  Space,
  message,
  Statistic,
  Row,
  Col,
} from "antd";
import {
  PlayCircleOutlined,
  StopOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useStore } from "../stores";
import { crawlerApi } from "../api";
import type { CrawlTask } from "../api";

const SUBDOMAIN_OPTIONS = [
  { value: "deep_learning", label: "深度学习" },
  { value: "nlp", label: "自然语言处理" },
  { value: "computer_vision", label: "计算机视觉" },
  { value: "reinforcement_learning", label: "强化学习" },
  { value: "graph_neural_networks", label: "图神经网络" },
  { value: "generative_models", label: "生成模型" },
  { value: "systems", label: "系统" },
];

const SOURCE_OPTIONS = [
  { value: "openalex", label: "OpenAlex（推荐，快速免费）" },
  { value: "semantic_scholar", label: "Semantic Scholar（需API Key）" },
  { value: "arxiv", label: "arXiv（前沿预印本，含引用交叉验证）" },
];

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  queued: { color: "default", label: "排队中" },
  running: { color: "processing", label: "运行中" },
  completed: { color: "success", label: "已完成" },
  failed: { color: "error", label: "失败" },
  cancelled: { color: "warning", label: "已取消" },
};

export default function CrawlerPage() {
  const { crawlTasks, activeCrawlTask, fetchCrawlTasks, startCrawl } =
    useStore();
  const [form] = Form.useForm();
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    fetchCrawlTasks();
  }, [fetchCrawlTasks]);

  const handleStart = async () => {
    try {
      const values = await form.validateFields();
      setStarting(true);
      await startCrawl(values);
      message.success("爬取任务已启动！");
    } catch {
      // validation error
    } finally {
      setStarting(false);
    }
  };

  const handleCancel = async (taskId: string) => {
    try {
      await crawlerApi.cancelTask(taskId);
      message.info("取消请求已发送");
      fetchCrawlTasks();
    } catch {
      message.error("取消失败");
    }
  };

  const active = activeCrawlTask;
  const isRunning = active?.status === "running" || active?.status === "queued";

  const columns = [
    {
      title: "状态",
      dataIndex: "status",
      width: 90,
      render: (s: string) => {
        const info = STATUS_MAP[s] || { color: "default", label: s };
        return <Tag color={info.color}>{info.label}</Tag>;
      },
    },
    { title: "领域", dataIndex: "domain", width: 120 },
    {
      title: "数据源",
      dataIndex: "source",
      width: 100,
      render: (s: string) => {
        const map: Record<string, string> = {
          openalex: "OpenAlex",
          semantic_scholar: "S2",
          arxiv: "arXiv",
        };
        return map[s] || s;
      },
    },
    { title: "子领域", dataIndex: "subdomain", width: 100 },
    {
      title: "进度",
      render: (_: unknown, r: CrawlTask) =>
        `搜索 ${r.searched} / 候选 ${r.candidates} / 入库 ${r.imported}`,
    },
    { title: "失败", dataIndex: "failed", width: 60 },
    {
      title: "时间",
      dataIndex: "created_at",
      width: 160,
      render: (t: string) => new Date(t).toLocaleString(),
    },
    {
      title: "操作",
      width: 80,
      render: (_: unknown, r: CrawlTask) =>
        ["running", "queued"].includes(r.status) ? (
          <Button
            size="small"
            danger
            icon={<StopOutlined />}
            onClick={() => handleCancel(r.id)}
          >
            取消
          </Button>
        ) : null,
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={16}>
        <Col span={14}>
          <Card title="启动爬取任务">
            <Form
              form={form}
              layout="inline"
              initialValues={{
                domain: "computer_science",
                subdomain: "deep_learning",
                source: "openalex",
                year_from: 2018,
                year_to: 2026,
                min_citations: 500,
                max_papers: 20,
              }}
              style={{ flexWrap: "wrap", gap: 8 }}
            >
              <Form.Item name="source" label="数据源">
                <Select
                  options={SOURCE_OPTIONS}
                  style={{ width: 250 }}
                />
              </Form.Item>
              <Form.Item name="subdomain" label="子领域">
                <Select
                  options={SUBDOMAIN_OPTIONS}
                  style={{ width: 150 }}
                  allowClear
                  placeholder="全部"
                />
              </Form.Item>
              <Form.Item name="year_from" label="起始年份">
                <InputNumber min={2000} max={2026} />
              </Form.Item>
              <Form.Item name="year_to" label="截止年份">
                <InputNumber min={2000} max={2026} />
              </Form.Item>
              <Form.Item name="min_citations" label="最低引用">
                <InputNumber min={0} step={100} />
              </Form.Item>
              <Form.Item name="max_papers" label="最大论文数">
                <InputNumber min={1} max={500} />
              </Form.Item>
              <Form.Item name="domain" hidden>
                <input />
              </Form.Item>
              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={handleStart}
                    loading={starting}
                    disabled={isRunning}
                  >
                    开始爬取
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={fetchCrawlTasks}
                  >
                    刷新
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col span={10}>
          {active && isRunning && (
            <Card title="当前任务进度" size="small">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic title="已搜索" value={active.searched} />
                </Col>
                <Col span={8}>
                  <Statistic title="候选" value={active.candidates} />
                </Col>
                <Col span={8}>
                  <Statistic title="已入库" value={active.imported} />
                </Col>
              </Row>
              <Progress
                percent={
                  active.candidates > 0
                    ? Math.round((active.imported / active.candidates) * 100)
                    : active.searched > 0
                    ? 30
                    : 5
                }
                status={active.status === "running" ? "active" : "normal"}
                style={{ marginTop: 12 }}
              />
            </Card>
          )}
        </Col>
      </Row>

      <Card title="历史任务" style={{ marginTop: 16 }}>
        <Table
          columns={columns}
          dataSource={crawlTasks}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}
