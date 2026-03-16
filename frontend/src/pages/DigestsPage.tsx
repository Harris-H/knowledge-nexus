import { useState, useEffect, useCallback } from "react";
import {
  Card, Button, Space, Tag, Typography, Spin, message, Popconfirm,
  Alert, Divider, List, Select, Empty, Tooltip, Row, Col, Statistic,
} from "antd";
import {
  ReloadOutlined, FileTextOutlined, BranchesOutlined,
  WarningOutlined, BulbOutlined, CheckCircleOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { digestsApi } from "../api";
import type { DomainDigest, CrossDomainAnalysis } from "../api";

const { Text, Title, Paragraph } = Typography;

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
  art: "🎨 艺术",
  cognitive_science: "🧩 认知科学",
  history: "📜 历史",
  life_science: "🔬 生命科学",
  medicine: "🏥 医学",
  military_science: "🎖️ 军事学",
};

export default function DigestsPage() {
  // --- 领域摘要列表 ---
  const [digests, setDigests] = useState<DomainDigest[]>([]);
  const [loading, setLoading] = useState(false);
  const [generatingDomain, setGeneratingDomain] = useState<string | null>(null);
  const [expandedDigest, setExpandedDigest] = useState<string | null>(null);

  // --- 跨域分析 ---
  const [crossDomainA, setCrossDomainA] = useState<string>("");
  const [crossDomainB, setCrossDomainB] = useState<string>("");
  const [crossAnalyzing, setCrossAnalyzing] = useState(false);
  const [crossResult, setCrossResult] = useState<CrossDomainAnalysis | null>(null);

  // 加载摘要列表
  const loadDigests = useCallback(async () => {
    setLoading(true);
    try {
      const res = await digestsApi.list();
      setDigests(res.data.items);
    } catch (e) {
      console.error("Failed to load digests:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadDigests(); }, [loadDigests]);

  // 统计
  const totalDomains = digests.length;
  const generatedCount = digests.filter((d) => d.digest_markdown).length;
  const staleCount = digests.filter((d) => d.digest_is_stale).length;

  // 生成单个领域摘要
  const handleGenerateDigest = async (domainName: string) => {
    setGeneratingDomain(domainName);
    try {
      await digestsApi.generate(domainName);
      message.success(`📝 ${DOMAIN_LABELS[domainName] || domainName} 摘要已生成`);
      await loadDigests();
    } catch (e: any) {
      message.error(`生成失败: ${e?.response?.data?.detail || e?.message}`);
    } finally {
      setGeneratingDomain(null);
    }
  };

  // 批量生成
  const handleGenerateAll = async () => {
    setGeneratingDomain("__all__");
    try {
      const res = await digestsApi.generateAll();
      message.success(`✅ 已生成 ${res.data.success}/${res.data.total} 个领域摘要`);
      await loadDigests();
    } catch (e: any) {
      message.error(`批量生成失败: ${e?.response?.data?.detail || e?.message}`);
    } finally {
      setGeneratingDomain(null);
    }
  };

  // 跨域分析
  const handleCrossDomainAnalysis = async () => {
    if (!crossDomainA || !crossDomainB) {
      message.warning("请选择两个领域");
      return;
    }
    setCrossAnalyzing(true);
    setCrossResult(null);
    try {
      const res = await digestsApi.crossDomainAnalysis(crossDomainA, crossDomainB);
      setCrossResult(res.data);
      message.success("🔗 跨域分析完成！");
    } catch (e: any) {
      message.error(`分析失败: ${e?.response?.data?.detail || e?.message}`);
    } finally {
      setCrossAnalyzing(false);
    }
  };

  // 领域选项（只显示有摘要的领域优先）
  const domainOptions = digests.map((d) => ({
    value: d.name,
    label: `${DOMAIN_LABELS[d.name] || d.name} (${d.digest_node_count}节点)`,
  }));

  return (
    <div style={{ padding: 16, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={4}>📋 领域知识摘要</Title>
      <Paragraph type="secondary">
        为每个知识领域生成 AI 摘要，浓缩核心概念、关键模式和跨域连接点。用于快速跨域关联分析。
      </Paragraph>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic title="领域总数" value={totalDomains} prefix={<BulbOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="已生成摘要"
              value={generatedCount}
              suffix={`/ ${totalDomains}`}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: generatedCount === totalDomains ? "#3f8600" : undefined }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="已过期"
              value={staleCount}
              prefix={<WarningOutlined />}
              valueStyle={{ color: staleCount > 0 ? "#cf1322" : "#3f8600" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadDigests} loading={loading} size="small">
                刷新
              </Button>
              <Popconfirm title="将为所有领域生成/重新生成摘要，可能需要几分钟" onConfirm={handleGenerateAll}>
                <Button type="primary" icon={<FileTextOutlined />} loading={generatingDomain === "__all__"} size="small">
                  一键生成全部
                </Button>
              </Popconfirm>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 跨域分析 */}
      <Card
        title={<><BranchesOutlined /> 基于摘要的跨域关联分析</>}
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Paragraph type="secondary" style={{ marginBottom: 12 }}>
          选择两个领域，AI 将基于预生成的摘要进行快速跨域分析。相比逐节点分析，更快速、视角更宏观。
        </Paragraph>
        <Space style={{ width: "100%" }} direction="vertical">
          <Row gutter={12}>
            <Col span={10}>
              <Select
                showSearch
                placeholder="选择领域 A"
                value={crossDomainA || undefined}
                onChange={setCrossDomainA}
                style={{ width: "100%" }}
                options={domainOptions}
                filterOption={(input, option) =>
                  (option?.label as string || "").toLowerCase().includes(input.toLowerCase())
                }
              />
            </Col>
            <Col span={10}>
              <Select
                showSearch
                placeholder="选择领域 B"
                value={crossDomainB || undefined}
                onChange={setCrossDomainB}
                style={{ width: "100%" }}
                options={domainOptions.filter((o) => o.value !== crossDomainA)}
                filterOption={(input, option) =>
                  (option?.label as string || "").toLowerCase().includes(input.toLowerCase())
                }
              />
            </Col>
            <Col span={4}>
              <Button
                type="primary"
                icon={<BranchesOutlined />}
                loading={crossAnalyzing}
                onClick={handleCrossDomainAnalysis}
                disabled={!crossDomainA || !crossDomainB}
                block
              >
                分析
              </Button>
            </Col>
          </Row>
        </Space>
      </Card>

      {/* 跨域分析结果 */}
      {crossAnalyzing && (
        <Card style={{ textAlign: "center", marginBottom: 16 }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>AI 正在基于领域摘要分析跨域关联...</Paragraph>
        </Card>
      )}

      {crossResult && (
        <Card
          title={`🔗 ${DOMAIN_LABELS[crossResult.domain_a] || crossResult.domain_a} ↔ ${DOMAIN_LABELS[crossResult.domain_b] || crossResult.domain_b} 跨域分析结果`}
          style={{ marginBottom: 16 }}
          extra={<Button size="small" onClick={() => setCrossResult(null)}>关闭</Button>}
        >
          {crossResult.summary && (
            <>
              <Alert type="success" message="📌 核心发现" description={crossResult.summary} style={{ marginBottom: 16 }} />
              <Divider />
            </>
          )}

          {crossResult.analogies?.length > 0 && (
            <>
              <Title level={5}>🪞 结构类比</Title>
              {crossResult.analogies.map((a, i) => (
                <Card key={i} size="small" style={{ marginBottom: 8 }}>
                  <Space style={{ marginBottom: 8 }}>
                    <Tag color="blue">{a.concept_a}</Tag>
                    <Text type="secondary">≈</Text>
                    <Tag color="purple">{a.concept_b}</Tag>
                    <Tag>{a.depth}</Tag>
                  </Space>
                  <Paragraph style={{ margin: 0, fontSize: 13 }}>{a.description}</Paragraph>
                </Card>
              ))}
              <Divider />
            </>
          )}

          {crossResult.transfer_ideas?.length > 0 && (
            <>
              <Title level={5}>🔄 知识迁移方向</Title>
              <List
                dataSource={crossResult.transfer_ideas}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <Space>
                          <Tag>{item.from_domain}</Tag>
                          <Text>→</Text>
                          <Tag>{item.to_domain}</Tag>
                          <Tag color={FEASIBILITY_COLORS[item.feasibility]}>{item.feasibility}</Tag>
                        </Space>
                      }
                      description={
                        <>
                          <Text type="secondary">源方法: {item.source_method} → 目标: {item.target_application}</Text>
                          <br />
                          {item.idea}
                        </>
                      }
                    />
                  </List.Item>
                )}
              />
              <Divider />
            </>
          )}

          {crossResult.unified_patterns?.length > 0 && (
            <>
              <Title level={5}><BulbOutlined /> 统一模式</Title>
              {crossResult.unified_patterns.map((p, i) => (
                <Card key={i} size="small" style={{ marginBottom: 8 }}>
                  <Title level={5} style={{ margin: 0 }}>{p.pattern_name}</Title>
                  <Paragraph style={{ fontSize: 13 }}>{p.description}</Paragraph>
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Text type="secondary">在 {DOMAIN_LABELS[crossResult.domain_a] || crossResult.domain_a} 中: {p.in_domain_a}</Text>
                    <Text type="secondary">在 {DOMAIN_LABELS[crossResult.domain_b] || crossResult.domain_b} 中: {p.in_domain_b}</Text>
                  </Space>
                </Card>
              ))}
              <Divider />
            </>
          )}

          {crossResult.new_hypotheses?.length > 0 && (
            <>
              <Title level={5}>🔬 新研究假设</Title>
              {crossResult.new_hypotheses.map((h, i) => (
                <Card key={i} size="small" style={{ marginBottom: 8 }} title={<Space><Tag color={FEASIBILITY_COLORS[h.impact]}>影响: {h.impact}</Tag>假设 {i + 1}</Space>}>
                  <Paragraph>{h.hypothesis}</Paragraph>
                  <Text type="secondary">推理依据: {h.basis}</Text>
                </Card>
              ))}
            </>
          )}
        </Card>
      )}

      {/* 领域摘要列表 */}
      <Divider orientation="left">各领域摘要详情</Divider>

      {loading && (
        <Card style={{ textAlign: "center" }}><Spin size="large" /></Card>
      )}

      {!loading && digests.length === 0 && (
        <Empty description="暂无领域数据，请先添加知识节点或论文" />
      )}

      {digests.map((d) => (
        <Card
          key={d.name}
          size="small"
          style={{ marginBottom: 12 }}
          title={
            <Space>
              <Text strong style={{ fontSize: 15 }}>{DOMAIN_LABELS[d.name] || d.name}</Text>
              {d.digest_markdown ? (
                <Tag color="green" icon={<CheckCircleOutlined />}>v{d.digest_version}</Tag>
              ) : (
                <Tag color="default">未生成</Tag>
              )}
              {d.digest_is_stale && (
                <Tooltip title="领域数据已变更，建议重新生成摘要">
                  <Tag icon={<WarningOutlined />} color="warning">已过期</Tag>
                </Tooltip>
              )}
              {d.digest_generated_at && (
                <Text type="secondary" style={{ fontSize: 11 }}>
                  <ClockCircleOutlined /> {new Date(d.digest_generated_at).toLocaleString()}
                </Text>
              )}
            </Space>
          }
          extra={
            <Space>
              {d.digest_markdown && (
                <Space split={<Divider type="vertical" />}>
                  <Text type="secondary" style={{ fontSize: 12 }}>{d.digest_node_count} 节点</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>{d.digest_paper_count} 论文</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>{d.digest_relation_count} 关联</Text>
                </Space>
              )}
              <Button
                size="small"
                icon={<ReloadOutlined />}
                loading={generatingDomain === d.name}
                onClick={() => handleGenerateDigest(d.name)}
              >
                {d.digest_markdown ? "重新生成" : "生成摘要"}
              </Button>
              {d.digest_markdown && (
                <Button
                  size="small"
                  type={expandedDigest === d.name ? "primary" : "default"}
                  onClick={() => setExpandedDigest(expandedDigest === d.name ? null : d.name)}
                >
                  {expandedDigest === d.name ? "收起" : "查看摘要"}
                </Button>
              )}
            </Space>
          }
        >
          {expandedDigest === d.name && d.digest_markdown && (
            <div
              style={{
                padding: "16px 20px",
                background: "#fafafa",
                borderRadius: 8,
                whiteSpace: "pre-wrap",
                fontSize: 13,
                lineHeight: 1.8,
                maxHeight: 600,
                overflow: "auto",
                border: "1px solid #f0f0f0",
              }}
            >
              {d.digest_markdown}
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}
