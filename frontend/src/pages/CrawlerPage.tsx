import { useCallback, useEffect, useState } from "react";
import {
  Card,
  Button,
  Form,
  InputNumber,
  Select,
  AutoComplete,
  Table,
  Tag,
  Progress,
  Space,
  message,
  Statistic,
  Row,
  Col,
  Tabs,
  Input,
  Descriptions,
  Spin,
} from "antd";
import {
  PlayCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  UserOutlined,
  BankOutlined,
  StarOutlined,
} from "@ant-design/icons";
import { useStore } from "../stores";
import { crawlerApi } from "../api";
import type {
  CrawlTask,
  ElitePreset,
  AuthorResult,
  InstitutionResult,
} from "../api";

const SUBDOMAIN_OPTIONS = [
  { value: "deep learning", label: "深度学习" },
  { value: "nlp", label: "自然语言处理" },
  { value: "computer vision", label: "计算机视觉" },
  { value: "reinforcement learning", label: "强化学习" },
  { value: "graph neural networks", label: "图神经网络" },
  { value: "generative models", label: "生成模型" },
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

const MODE_MAP: Record<string, { label: string; color: string }> = {
  keyword: { label: "关键词", color: "blue" },
  author: { label: "学者", color: "purple" },
  institution: { label: "机构", color: "cyan" },
  elite_preset: { label: "预设", color: "gold" },
};

// ── Keyword Form ──
function KeywordForm({
  onStart,
  starting,
  isRunning,
  onRefresh,
}: {
  onStart: (values: Record<string, unknown>) => void;
  starting: boolean;
  isRunning: boolean;
  onRefresh: () => void;
}) {
  const [form] = Form.useForm();

  const handleStart = async () => {
    const values = await form.validateFields();
    onStart({ ...values, mode: "keyword" });
  };

  return (
    <Form
      form={form}
      layout="inline"
      initialValues={{
        domain: "computer_science",
        subdomain: "deep learning",
        source: "openalex",
        year_from: 2018,
        year_to: 2026,
        min_citations: 0,
        max_papers: 20,
      }}
      style={{ flexWrap: "wrap", gap: 8 }}
    >
      <Form.Item name="source" label="数据源">
        <Select options={SOURCE_OPTIONS} style={{ width: 250 }} />
      </Form.Item>
      <Form.Item name="subdomain" label="子领域">
        <AutoComplete
          options={SUBDOMAIN_OPTIONS}
          style={{ width: 200 }}
          placeholder="选择或输入关键词"
          allowClear
          filterOption={(inputValue, option) => {
            const isPreset = SUBDOMAIN_OPTIONS.some(
              (o) => o.value === inputValue,
            );
            if (isPreset) return true;
            const label = ((option?.label as string) ?? "").toLowerCase();
            const value = ((option?.value as string) ?? "").toLowerCase();
            const input = inputValue.toLowerCase();
            return label.includes(input) || value.includes(input);
          }}
        />
      </Form.Item>
      <Form.Item name="year_from" label="起始年份">
        <InputNumber min={2000} max={2026} />
      </Form.Item>
      <Form.Item name="year_to" label="截止年份">
        <InputNumber min={2000} max={2026} />
      </Form.Item>
      <Form.Item
        name="min_citations"
        label="最低引用"
        tooltip="设为 0 则按引用量降序取 Top N"
      >
        <InputNumber min={0} step={100} />
      </Form.Item>
      <Form.Item
        name="max_papers"
        label="获取数量"
        tooltip="最多获取前 N 篇论文"
      >
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
          <Button icon={<ReloadOutlined />} onClick={onRefresh}>
            刷新
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
}

// ── Elite Form ──
function EliteForm({
  onStart,
  starting,
  isRunning,
  onRefresh,
}: {
  onStart: (values: Record<string, unknown>) => void;
  starting: boolean;
  isRunning: boolean;
  onRefresh: () => void;
}) {
  const [eliteMode, setEliteMode] = useState<string>("elite_preset");
  const [presets, setPresets] = useState<Record<string, ElitePreset>>({});
  const [presetsLoading, setPresetsLoading] = useState(false);

  // Author search
  const [authorOptions, setAuthorOptions] = useState<AuthorResult[]>([]);
  const [authorSearching, setAuthorSearching] = useState(false);
  const [selectedAuthor, setSelectedAuthor] = useState<AuthorResult | null>(
    null,
  );

  // Institution search
  const [instOptions, setInstOptions] = useState<InstitutionResult[]>([]);
  const [instSearching, setInstSearching] = useState(false);
  const [selectedInst, setSelectedInst] = useState<InstitutionResult | null>(
    null,
  );

  // Common params
  const [yearFrom, setYearFrom] = useState(2020);
  const [yearTo, setYearTo] = useState(2026);
  const [minCitations, setMinCitations] = useState(50);
  const [maxPapers, setMaxPapers] = useState(50);
  const [presetName, setPresetName] = useState<string>("");

  useEffect(() => {
    setPresetsLoading(true);
    crawlerApi
      .listPresets()
      .then(({ data }) => {
        setPresets(data);
        const keys = Object.keys(data);
        if (keys.length > 0) setPresetName(keys[0]);
      })
      .finally(() => setPresetsLoading(false));
  }, []);

  const handleAuthorSearch = useCallback(async (value: string) => {
    if (value.length < 2) return;
    setAuthorSearching(true);
    try {
      const { data } = await crawlerApi.searchAuthors(value);
      setAuthorOptions(data);
    } finally {
      setAuthorSearching(false);
    }
  }, []);

  const handleInstSearch = useCallback(async (value: string) => {
    if (value.length < 2) return;
    setInstSearching(true);
    try {
      const { data } = await crawlerApi.searchInstitutions(value);
      setInstOptions(data);
    } finally {
      setInstSearching(false);
    }
  }, []);

  const handleStart = () => {
    const base = {
      mode: eliteMode,
      domain: "computer_science",
      source: "openalex",
      year_from: yearFrom,
      year_to: yearTo,
      min_citations: minCitations,
      max_papers: maxPapers,
    };

    if (eliteMode === "author") {
      if (!selectedAuthor) {
        message.warning("请先搜索并选择一位学者");
        return;
      }
      onStart({ ...base, author_id: selectedAuthor.id });
    } else if (eliteMode === "institution") {
      if (!selectedInst) {
        message.warning("请先搜索并选择一个机构");
        return;
      }
      onStart({ ...base, institution_id: selectedInst.id });
    } else {
      if (!presetName) {
        message.warning("请选择一个预设配置");
        return;
      }
      onStart({ ...base, preset_name: presetName });
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Space wrap size="middle">
        <span style={{ fontWeight: 500 }}>搜索模式：</span>
        <Select
          value={eliteMode}
          onChange={setEliteMode}
          style={{ width: 180 }}
          options={[
            {
              value: "elite_preset",
              label: (
                <span>
                  <StarOutlined /> 预设配置
                </span>
              ),
            },
            {
              value: "author",
              label: (
                <span>
                  <UserOutlined /> 按学者搜索
                </span>
              ),
            },
            {
              value: "institution",
              label: (
                <span>
                  <BankOutlined /> 按机构搜索
                </span>
              ),
            },
          ]}
        />
        <InputNumber
          addonBefore="起始"
          value={yearFrom}
          onChange={(v) => setYearFrom(v ?? 2020)}
          min={2000}
          max={2026}
          style={{ width: 130 }}
        />
        <InputNumber
          addonBefore="截止"
          value={yearTo}
          onChange={(v) => setYearTo(v ?? 2026)}
          min={2000}
          max={2026}
          style={{ width: 130 }}
        />
        <InputNumber
          addonBefore="最低引用"
          value={minCitations}
          onChange={(v) => setMinCitations(v ?? 0)}
          min={0}
          step={50}
          style={{ width: 160 }}
        />
        <InputNumber
          addonBefore="数量"
          value={maxPapers}
          onChange={(v) => setMaxPapers(v ?? 50)}
          min={1}
          max={500}
          style={{ width: 130 }}
        />
      </Space>

      {/* Preset Mode */}
      {eliteMode === "elite_preset" && (
        <Spin spinning={presetsLoading}>
          <Space direction="vertical" style={{ width: "100%" }}>
            <Select
              value={presetName}
              onChange={setPresetName}
              style={{ width: 300 }}
              placeholder="选择预设配置"
              options={Object.entries(presets).map(([key, val]) => ({
                value: key,
                label: `${key} — ${val.description}`,
              }))}
            />
            {presetName && presets[presetName] && (
              <Descriptions size="small" column={4} bordered>
                <Descriptions.Item label="说明">
                  {presets[presetName].description}
                </Descriptions.Item>
                <Descriptions.Item label="学者数">
                  {presets[presetName].researchers}
                </Descriptions.Item>
                <Descriptions.Item label="机构数">
                  {presets[presetName].institutions}
                </Descriptions.Item>
                <Descriptions.Item label="最低引用">
                  {presets[presetName].min_citations}
                </Descriptions.Item>
              </Descriptions>
            )}
          </Space>
        </Spin>
      )}

      {/* Author Mode */}
      {eliteMode === "author" && (
        <Space direction="vertical" style={{ width: "100%" }}>
          <Input.Search
            placeholder="输入学者姓名，如 Geoffrey Hinton"
            onSearch={handleAuthorSearch}
            loading={authorSearching}
            enterButton="搜索"
            style={{ maxWidth: 400 }}
          />
          {authorOptions.length > 0 && (
            <Table
              size="small"
              rowKey="id"
              dataSource={authorOptions}
              pagination={false}
              rowSelection={{
                type: "radio",
                selectedRowKeys: selectedAuthor ? [selectedAuthor.id] : [],
                onChange: (_, rows) => setSelectedAuthor(rows[0] || null),
              }}
              columns={[
                { title: "姓名", dataIndex: "name", width: 180 },
                { title: "机构", dataIndex: "affiliation", ellipsis: true },
                { title: "h-index", dataIndex: "h_index", width: 80 },
                {
                  title: "总引用",
                  dataIndex: "cited_by_count",
                  width: 100,
                  render: (v: number) => v.toLocaleString(),
                },
                {
                  title: "ID",
                  dataIndex: "id",
                  width: 140,
                  render: (v: string) => (
                    <Tag style={{ fontSize: 11 }}>{v}</Tag>
                  ),
                },
              ]}
            />
          )}
        </Space>
      )}

      {/* Institution Mode */}
      {eliteMode === "institution" && (
        <Space direction="vertical" style={{ width: "100%" }}>
          <Input.Search
            placeholder="输入机构名称，如 Stanford University"
            onSearch={handleInstSearch}
            loading={instSearching}
            enterButton="搜索"
            style={{ maxWidth: 400 }}
          />
          {instOptions.length > 0 && (
            <Table
              size="small"
              rowKey="id"
              dataSource={instOptions}
              pagination={false}
              rowSelection={{
                type: "radio",
                selectedRowKeys: selectedInst ? [selectedInst.id] : [],
                onChange: (_, rows) => setSelectedInst(rows[0] || null),
              }}
              columns={[
                { title: "名称", dataIndex: "name", width: 250 },
                { title: "国家", dataIndex: "country", width: 60 },
                {
                  title: "论文数",
                  dataIndex: "works_count",
                  width: 100,
                  render: (v: number) => v.toLocaleString(),
                },
                {
                  title: "总引用",
                  dataIndex: "cited_by_count",
                  width: 120,
                  render: (v: number) => v.toLocaleString(),
                },
                {
                  title: "ID",
                  dataIndex: "id",
                  width: 130,
                  render: (v: string) => (
                    <Tag style={{ fontSize: 11 }}>{v}</Tag>
                  ),
                },
              ]}
            />
          )}
        </Space>
      )}

      <Space>
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={handleStart}
          loading={starting}
          disabled={isRunning}
        >
          开始精英爬取
        </Button>
        <Button icon={<ReloadOutlined />} onClick={onRefresh}>
          刷新
        </Button>
      </Space>
    </div>
  );
}

// ── Main Page ──
export default function CrawlerPage() {
  const { crawlTasks, activeCrawlTask, fetchCrawlTasks, startCrawl } =
    useStore();
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    fetchCrawlTasks();
  }, [fetchCrawlTasks]);

  const handleStart = async (values: Record<string, unknown>) => {
    try {
      setStarting(true);
      await startCrawl(values);
      message.success("爬取任务已启动！");
    } catch {
      message.error("启动失败");
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
    {
      title: "模式",
      dataIndex: "mode",
      width: 80,
      render: (s: string) => {
        const info = MODE_MAP[s] || { label: s, color: "default" };
        return <Tag color={info.color}>{info.label}</Tag>;
      },
    },
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
    {
      title: "目标",
      width: 160,
      render: (_: unknown, r: CrawlTask) => {
        if (r.mode === "author" && r.author_id) return r.author_id;
        if (r.mode === "institution" && r.institution_id)
          return r.institution_id;
        if (r.mode === "elite_preset" && r.preset_name) return r.preset_name;
        return r.subdomain || r.domain;
      },
    },
    {
      title: "进度",
      render: (_: unknown, r: CrawlTask) => {
        const skipped = r.candidates - r.imported - r.failed;
        const parts = [
          `搜索 ${r.searched}`,
          `候选 ${r.candidates}`,
          `入库 ${r.imported}`,
        ];
        if (skipped > 0) parts.push(`重复 ${skipped}`);
        if (r.failed > 0) parts.push(`失败 ${r.failed}`);
        return parts.join(" / ");
      },
    },
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

  const tabItems = [
    {
      key: "keyword",
      label: "🔍 关键词搜索",
      children: (
        <KeywordForm
          onStart={handleStart}
          starting={starting}
          isRunning={isRunning}
          onRefresh={fetchCrawlTasks}
        />
      ),
    },
    {
      key: "elite",
      label: "⭐ 精英搜索",
      children: (
        <EliteForm
          onStart={handleStart}
          starting={starting}
          isRunning={isRunning}
          onRefresh={fetchCrawlTasks}
        />
      ),
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={16}>
        <Col span={active && isRunning ? 14 : 24}>
          <Card>
            <Tabs items={tabItems} />
          </Card>
        </Col>

        {active && isRunning && (
          <Col span={10}>
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
          </Col>
        )}
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
