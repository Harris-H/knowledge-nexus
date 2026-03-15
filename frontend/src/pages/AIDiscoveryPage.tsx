import { useState, useEffect, useCallback } from "react";
import {
  Card, Button, Space, Tag, Typography, Spin, message, Popconfirm,
  Alert, Divider, Progress, List, Select, Tabs, AutoComplete,
} from "antd";
import {
  ThunderboltOutlined, SaveOutlined, ExperimentOutlined, BulbOutlined,
  CheckCircleOutlined, SearchOutlined,
} from "@ant-design/icons";
import { aiApi } from "../api";
import type { AIDiscovery, DeriveResult, PairAnalysis } from "../api";

const { Text, Title, Paragraph } = Typography;

const RELATION_TYPE_COLORS: Record<string, string> = {
  INSPIRES: "orange",
  ANALOGOUS_TO: "blue",
  RELATED_TO: "cyan",
  BUILDS_ON: "purple",
  IMPROVES: "green",
  ENABLES: "volcano",
  PART_OF: "lime",
};

const FEASIBILITY_COLORS: Record<string, string> = {
  high: "green",
  medium: "gold",
  low: "red",
};

const DOMAIN_LABELS: Record<string, string> = {
  computer_science: "💻 计算机",
  speech_ai: "🎤 语音AI",
  biology: "🧬 生物学",
  physics: "⚛️ 物理学",
  mathematics: "📊 数学",
  neuroscience: "🧠 神经科学",
  chemistry: "🧪 化学",
  engineering: "⚙️ 工程学",
  psychology: "🧠 心理学",
  ecology: "🌍 生态学",
  philosophy: "🤔 哲学",
  sociology: "👥 社会学",
  economics: "📈 经济学",
};

interface NodeItem {
  id: string; name: string; type: string; node_type: string;
  domain: string; summary: string;
}

export default function AIDiscoveryPage() {
  // --- 通用状态 ---
  const [allNodes, setAllNodes] = useState<NodeItem[]>([]);
  const [domainCounts, setDomainCounts] = useState<Record<string, number>>({});

  // --- 发现关联 ---
  const [discovering, setDiscovering] = useState(false);
  const [discoveries, setDiscoveries] = useState<AIDiscovery[]>([]);
  const [totalNodes, setTotalNodes] = useState(0);
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  // --- 推导新知识 ---
  const [deriving, setDeriving] = useState(false);
  const [deriveResult, setDeriveResult] = useState<DeriveResult | null>(null);
  const [deriveNodeIds, setDeriveNodeIds] = useState<string[]>([]);

  // --- 配对分析 ---
  const [pairAnalyzing, setPairAnalyzing] = useState(false);
  const [pairResult, setPairResult] = useState<PairAnalysis | null>(null);
  const [pairNodeA, setPairNodeA] = useState<string>("");
  const [pairNodeB, setPairNodeB] = useState<string>("");

  // 加载节点列表
  const loadNodes = useCallback(async () => {
    try {
      const res = await aiApi.listNodes();
      setAllNodes(res.data.items);
      setDomainCounts(res.data.domain_counts);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { loadNodes(); }, [loadNodes]);

  // --- 发现关联 ---
  const handleDiscover = async () => {
    setDiscovering(true);
    setDiscoveries([]);
    setSavedIds(new Set());
    try {
      const res = await aiApi.discover(10, selectedDomains);
      setDiscoveries(res.data.discoveries);
      setTotalNodes(res.data.total_nodes);
      if (res.data.discoveries.length === 0) {
        message.info("AI 未发现新的关联，知识网络已经很完善了！");
      } else {
        message.success(`🔍 发现 ${res.data.discoveries.length} 条新关联！`);
      }
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message || "未知错误";
      message.error(`发现失败: ${detail}`);
    } finally {
      setDiscovering(false);
    }
  };

  const handleSaveAll = async (autoConfirm: boolean) => {
    try {
      const res = await aiApi.saveDiscoveries(discoveries, autoConfirm);
      message.success(`已保存 ${res.data.saved} 条关联${autoConfirm ? "（已确认）" : "（待审核）"}`);
      setSavedIds(new Set(discoveries.map((_, i) => i)));
    } catch {
      message.error("保存失败");
    }
  };

  // --- 推导新知识 ---
  const handleDerive = async () => {
    const ids = deriveNodeIds.length > 0
      ? deriveNodeIds
      : [...new Set(discoveries.flatMap((d) => [d.source_id, d.target_id]))].slice(0, 10);
    if (ids.length === 0) {
      message.warning("请先选择节点或运行「发现关联」");
      return;
    }
    setDeriving(true);
    setDeriveResult(null);
    try {
      const res = await aiApi.derive(ids);
      setDeriveResult(res.data);
      message.success("🧠 知识推导完成！");
    } catch (e: any) {
      message.error(`推导失败: ${e?.response?.data?.detail || e?.message}`);
    } finally {
      setDeriving(false);
    }
  };

  // --- 配对分析 ---
  const handlePairAnalysis = async () => {
    if (!pairNodeA || !pairNodeB) {
      message.warning("请选择两个节点");
      return;
    }
    setPairAnalyzing(true);
    setPairResult(null);
    try {
      const res = await aiApi.analyzePair(pairNodeA, pairNodeB);
      setPairResult(res.data);
      message.success("🔬 分析完成！");
    } catch (e: any) {
      message.error(`分析失败: ${e?.response?.data?.detail || e?.message}`);
    } finally {
      setPairAnalyzing(false);
    }
  };

  // --- 节点搜索选项 ---
  const nodeOptions = allNodes.map((n) => ({
    value: n.id,
    label: `${n.name} [${DOMAIN_LABELS[n.domain] || n.domain}]`,
  }));

  const filterOption = (inputValue: string, option?: { label: string }) =>
    (option?.label || "").toLowerCase().includes(inputValue.toLowerCase());

  return (
    <div style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
      <Title level={4}>🤖 AI 知识发现引擎</Title>
      <Paragraph type="secondary">
        利用大模型分析知识库中 {allNodes.length} 个节点，自动发现跨领域关联和推导新知识。
      </Paragraph>

      <Tabs
        defaultActiveKey="discover"
        items={[
          {
            key: "discover",
            label: "🔍 发现关联",
            children: (
              <>
                {/* 领域选择 */}
                <Card size="small" style={{ marginBottom: 16 }}>
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Text strong>选择分析领域（留空=全部）：</Text>
                    <Select
                      mode="multiple"
                      placeholder="全部领域"
                      value={selectedDomains}
                      onChange={setSelectedDomains}
                      style={{ width: "100%" }}
                      options={Object.entries(domainCounts).map(([d, c]) => ({
                        value: d,
                        label: `${DOMAIN_LABELS[d] || d} (${c}个节点)`,
                      }))}
                    />
                    <Space>
                      <Button
                        type="primary"
                        icon={<ThunderboltOutlined />}
                        loading={discovering}
                        onClick={handleDiscover}
                      >
                        开始发现
                      </Button>
                      {selectedDomains.length > 0 && (
                        <Text type="secondary">
                          将在 {selectedDomains.map(d => DOMAIN_LABELS[d] || d).join("、")} 领域中搜索
                        </Text>
                      )}
                    </Space>
                  </Space>
                </Card>

                {/* 发现中 */}
                {discovering && (
                  <Card style={{ marginBottom: 16, textAlign: "center" }}>
                    <Spin size="large" />
                    <Paragraph style={{ marginTop: 16 }}>
                      AI 正在分析 {totalNodes || "全部"} 个知识节点...（约 10-30 秒）
                    </Paragraph>
                  </Card>
                )}

                {/* 发现结果 */}
                {discoveries.length > 0 && (
                  <Card
                    title={`🔍 发现 ${discoveries.length} 条跨域关联`}
                    style={{ marginBottom: 16 }}
                    extra={
                      <Space>
                        <Popconfirm title="保存为待审核？" onConfirm={() => handleSaveAll(false)}>
                          <Button icon={<SaveOutlined />} size="small">待审核</Button>
                        </Popconfirm>
                        <Popconfirm title="直接确认入库？" onConfirm={() => handleSaveAll(true)}>
                          <Button type="primary" icon={<CheckCircleOutlined />} size="small">确认入库</Button>
                        </Popconfirm>
                      </Space>
                    }
                  >
                    {discoveries.map((d, i) => (
                      <div
                        key={i}
                        style={{
                          padding: "12px 0",
                          borderBottom: i < discoveries.length - 1 ? "1px solid #f0f0f0" : "none",
                          opacity: savedIds.has(i) ? 0.5 : 1,
                        }}
                      >
                        <Space wrap>
                          <Tag color={RELATION_TYPE_COLORS[d.relation_type] || "default"}>{d.relation_type}</Tag>
                          <Text strong>{d.source_name}</Text>
                          <Text type="secondary">→</Text>
                          <Text strong>{d.target_name}</Text>
                          <Progress
                            type="circle" percent={Math.round(d.confidence * 100)} size={28}
                            strokeColor={d.confidence >= 0.8 ? "#52c41a" : d.confidence >= 0.6 ? "#faad14" : "#ff4d4f"}
                          />
                          {savedIds.has(i) && <Tag color="green">已保存</Tag>}
                        </Space>
                        <Paragraph style={{ marginTop: 4, marginBottom: 2, fontSize: 13 }}>{d.description}</Paragraph>
                        {d.insight && <Text type="secondary" style={{ fontSize: 12 }}>💡 {d.insight}</Text>}
                      </div>
                    ))}
                  </Card>
                )}
              </>
            ),
          },
          {
            key: "pair",
            label: "🔬 配对分析",
            children: (
              <>
                <Card size="small" style={{ marginBottom: 16 }}>
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Text strong>选择两个节点进行深度关联分析：</Text>
                    <Space style={{ width: "100%" }} direction="vertical">
                      <Select
                        showSearch
                        placeholder="节点 A"
                        value={pairNodeA || undefined}
                        onChange={setPairNodeA}
                        options={nodeOptions}
                        filterOption={filterOption}
                        style={{ width: "100%" }}
                      />
                      <Select
                        showSearch
                        placeholder="节点 B"
                        value={pairNodeB || undefined}
                        onChange={setPairNodeB}
                        options={nodeOptions}
                        filterOption={filterOption}
                        style={{ width: "100%" }}
                      />
                    </Space>
                    <Button
                      type="primary"
                      icon={<SearchOutlined />}
                      loading={pairAnalyzing}
                      onClick={handlePairAnalysis}
                      disabled={!pairNodeA || !pairNodeB}
                    >
                      深度分析
                    </Button>
                  </Space>
                </Card>

                {pairAnalyzing && (
                  <Card style={{ textAlign: "center" }}><Spin size="large" /><Paragraph style={{ marginTop: 16 }}>分析中...</Paragraph></Card>
                )}

                {pairResult && (
                  <Card title="🔬 配对分析结果" style={{ marginBottom: 16 }}>
                    <Space style={{ marginBottom: 12 }}>
                      <Tag color={pairResult.has_relation ? "green" : "red"}>
                        {pairResult.has_relation ? "✅ 存在关联" : "❌ 无明显关联"}
                      </Tag>
                      <Tag color={RELATION_TYPE_COLORS[pairResult.relation_type] || "default"}>{pairResult.relation_type}</Tag>
                      <Progress type="circle" percent={Math.round(pairResult.confidence * 100)} size={32} />
                    </Space>
                    <Paragraph><Text strong>关联描述：</Text>{pairResult.description}</Paragraph>
                    <Divider />
                    <Paragraph><Text strong>🏗️ 结构类比：</Text>{pairResult.structural_analogy}</Paragraph>
                    <Paragraph><Text strong>🔗 因果联系：</Text>{pairResult.causal_link}</Paragraph>
                    <Paragraph><Text strong>🤝 互补性：</Text>{pairResult.complementarity}</Paragraph>
                    <Paragraph><Text strong>🎯 统一框架：</Text>{pairResult.unified_framework}</Paragraph>
                    <Divider />
                    <Alert type="success" message={`💡 新启示：${pairResult.new_insight}`} />
                  </Card>
                )}
              </>
            ),
          },
          {
            key: "derive",
            label: "🧠 推导知识",
            children: (
              <>
                <Card size="small" style={{ marginBottom: 16 }}>
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Text strong>选择知识节点进行深度推导（2-10个）：</Text>
                    <Select
                      mode="multiple"
                      placeholder="搜索并选择节点..."
                      value={deriveNodeIds}
                      onChange={setDeriveNodeIds}
                      options={nodeOptions}
                      filterOption={filterOption}
                      style={{ width: "100%" }}
                      maxCount={10}
                    />
                    <Button
                      type="primary"
                      icon={<ExperimentOutlined />}
                      loading={deriving}
                      onClick={handleDerive}
                      disabled={deriveNodeIds.length === 0 && discoveries.length === 0}
                    >
                      {deriveNodeIds.length > 0
                        ? `推导 ${deriveNodeIds.length} 个节点的深层知识`
                        : "用发现结果中的节点推导"}
                    </Button>
                  </Space>
                </Card>

                {deriving && (
                  <Card style={{ textAlign: "center" }}><Spin size="large" /><Paragraph style={{ marginTop: 16 }}>深度推导中...</Paragraph></Card>
                )}

                {deriveResult && (
                  <Card title="🧠 知识推导结果" style={{ marginBottom: 16 }}>
                    {deriveResult.abstract_pattern && (
                      <>
                        <Title level={5}><BulbOutlined /> 深层模式：{deriveResult.abstract_pattern.name}</Title>
                        <Paragraph>{deriveResult.abstract_pattern.description}</Paragraph>
                        <Divider />
                      </>
                    )}
                    {deriveResult.transfer_ideas && deriveResult.transfer_ideas.length > 0 && (
                      <>
                        <Title level={5}>🔄 知识迁移方向</Title>
                        <List
                          dataSource={deriveResult.transfer_ideas}
                          renderItem={(item) => (
                            <List.Item>
                              <List.Item.Meta
                                title={<Space><Tag>{item.from_domain}</Tag><Text>→</Text><Tag>{item.to_domain}</Tag><Tag color={FEASIBILITY_COLORS[item.feasibility]}>{item.feasibility}</Tag></Space>}
                                description={item.idea}
                              />
                            </List.Item>
                          )}
                        />
                        <Divider />
                      </>
                    )}
                    {deriveResult.missing_links && deriveResult.missing_links.length > 0 && (
                      <>
                        <Title level={5}>🔗 缺失环节</Title>
                        {deriveResult.missing_links.map((link, i) => (
                          <Alert key={i} type="warning" showIcon message={link.description} description={`潜在价值: ${link.potential_value}`} style={{ marginBottom: 8 }} />
                        ))}
                        <Divider />
                      </>
                    )}
                    {deriveResult.new_hypotheses && deriveResult.new_hypotheses.length > 0 && (
                      <>
                        <Title level={5}>🔬 新研究假设</Title>
                        {deriveResult.new_hypotheses.map((h, i) => (
                          <Card key={i} size="small" style={{ marginBottom: 8 }} title={<Space><Tag color={FEASIBILITY_COLORS[h.impact]}>影响: {h.impact}</Tag>假设 {i + 1}</Space>}>
                            <Paragraph>{h.hypothesis}</Paragraph>
                            <Text type="secondary">验证方法: {h.evidence_needed}</Text>
                          </Card>
                        ))}
                      </>
                    )}
                  </Card>
                )}
              </>
            ),
          },
        ]}
      />
    </div>
  );
}
