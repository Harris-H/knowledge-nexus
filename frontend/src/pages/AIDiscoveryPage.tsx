import { useState } from "react";
import {
  Card, Button, Space, Tag, Typography, Spin, message, Popconfirm,
  Alert, Collapse, Divider, Progress, List,
} from "antd";
import {
  ThunderboltOutlined, SaveOutlined, ExperimentOutlined, BulbOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { aiApi } from "../api";
import type { AIDiscovery, DeriveResult } from "../api";

const { Text, Title, Paragraph } = Typography;

const RELATION_TYPE_COLORS: Record<string, string> = {
  INSPIRES: "orange",
  ANALOGOUS_TO: "blue",
  RELATED_TO: "cyan",
  BUILDS_ON: "purple",
};

const FEASIBILITY_COLORS: Record<string, string> = {
  high: "green",
  medium: "gold",
  low: "red",
};

export default function AIDiscoveryPage() {
  const [discovering, setDiscovering] = useState(false);
  const [discoveries, setDiscoveries] = useState<AIDiscovery[]>([]);
  const [totalNodes, setTotalNodes] = useState(0);
  const [deriving, setDeriving] = useState(false);
  const [deriveResult, setDeriveResult] = useState<DeriveResult | null>(null);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  const handleDiscover = async () => {
    setDiscovering(true);
    setDiscoveries([]);
    try {
      const res = await aiApi.discover(10);
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

  const handleSaveAll = async () => {
    try {
      const res = await aiApi.saveDiscoveries(discoveries, false);
      message.success(`已保存 ${res.data.saved} 条关联（待审核状态）`);
      setSavedIds(new Set(discoveries.map((_, i) => i)));
    } catch {
      message.error("保存失败");
    }
  };

  const handleSaveAndConfirm = async () => {
    try {
      const res = await aiApi.saveDiscoveries(discoveries, true);
      message.success(`已保存并确认 ${res.data.saved} 条关联`);
      setSavedIds(new Set(discoveries.map((_, i) => i)));
    } catch {
      message.error("保存失败");
    }
  };

  const handleDerive = async () => {
    setDeriving(true);
    setDeriveResult(null);
    try {
      // 用发现的关联中涉及的节点做推导
      const nodeIds = new Set<string>();
      discoveries.forEach((d) => {
        nodeIds.add(d.source_id);
        nodeIds.add(d.target_id);
      });
      // 如果没有发现结果，用空数组触发全局推导
      const ids = nodeIds.size > 0 ? Array.from(nodeIds).slice(0, 10) : [];
      if (ids.length === 0) {
        message.warning("请先运行「发现关联」获取一些知识节点");
        setDeriving(false);
        return;
      }
      const res = await aiApi.derive(ids);
      setDeriveResult(res.data);
      message.success("🧠 知识推导完成！");
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message || "未知错误";
      message.error(`推导失败: ${detail}`);
    } finally {
      setDeriving(false);
    }
  };

  return (
    <div style={{ padding: 16, maxWidth: 1000, margin: "0 auto" }}>
      <Title level={4}>🤖 AI 知识发现引擎</Title>
      <Paragraph type="secondary">
        利用大模型分析知识库中的所有节点和论文，自动发现跨领域的深层关联，并推导新知识。
      </Paragraph>

      {/* 操作按钮 */}
      <Space style={{ marginBottom: 16 }} wrap>
        <Button
          type="primary"
          icon={<ThunderboltOutlined />}
          loading={discovering}
          onClick={handleDiscover}
          size="large"
        >
          🔍 发现跨域关联
        </Button>
        <Button
          icon={<ExperimentOutlined />}
          loading={deriving}
          onClick={handleDerive}
          disabled={discoveries.length === 0}
          size="large"
        >
          🧠 推导新知识
        </Button>
      </Space>

      {/* 发现中 */}
      {discovering && (
        <Card style={{ marginBottom: 16, textAlign: "center" }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>
            AI 正在扫描 {totalNodes || "所有"} 个知识节点，发现跨域关联...
          </Paragraph>
          <Paragraph type="secondary">这可能需要 10-30 秒</Paragraph>
        </Card>
      )}

      {/* 发现结果 */}
      {discoveries.length > 0 && (
        <Card
          title={`🔍 发现 ${discoveries.length} 条跨域关联`}
          style={{ marginBottom: 16 }}
          extra={
            <Space>
              <Popconfirm
                title="保存为待审核状态？"
                onConfirm={handleSaveAll}
              >
                <Button icon={<SaveOutlined />} size="small">
                  保存（待审核）
                </Button>
              </Popconfirm>
              <Popconfirm
                title="直接保存并确认？"
                description="将直接出现在知识图谱中"
                onConfirm={handleSaveAndConfirm}
              >
                <Button type="primary" icon={<CheckCircleOutlined />} size="small">
                  保存并确认
                </Button>
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
              <Space align="start" style={{ width: "100%" }}>
                <div style={{ flex: 1 }}>
                  <Space wrap>
                    <Tag color={RELATION_TYPE_COLORS[d.relation_type] || "default"}>
                      {d.relation_type}
                    </Tag>
                    <Text strong>{d.source_name}</Text>
                    <Text type="secondary">→</Text>
                    <Text strong>{d.target_name}</Text>
                    <Progress
                      type="circle"
                      percent={Math.round(d.confidence * 100)}
                      size={28}
                      strokeColor={d.confidence >= 0.8 ? "#52c41a" : d.confidence >= 0.6 ? "#faad14" : "#ff4d4f"}
                    />
                    {savedIds.has(i) && <Tag color="green">已保存</Tag>}
                  </Space>
                  <Paragraph
                    style={{ marginTop: 4, marginBottom: 2, fontSize: 13 }}
                  >
                    {d.description}
                  </Paragraph>
                  {d.insight && (
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      💡 {d.insight}
                    </Text>
                  )}
                </div>
              </Space>
            </div>
          ))}
        </Card>
      )}

      {/* 推导中 */}
      {deriving && (
        <Card style={{ marginBottom: 16, textAlign: "center" }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>
            AI 正在进行深度知识推导...
          </Paragraph>
        </Card>
      )}

      {/* 推导结果 */}
      {deriveResult && (
        <Card title="🧠 知识推导结果" style={{ marginBottom: 16 }}>
          {/* 本质模式 */}
          {deriveResult.abstract_pattern && (
            <>
              <Title level={5}>
                <BulbOutlined /> 深层模式：{deriveResult.abstract_pattern.name}
              </Title>
              <Paragraph>{deriveResult.abstract_pattern.description}</Paragraph>
              <Divider />
            </>
          )}

          {/* 迁移想法 */}
          {deriveResult.transfer_ideas && deriveResult.transfer_ideas.length > 0 && (
            <>
              <Title level={5}>🔄 知识迁移方向</Title>
              <List
                dataSource={deriveResult.transfer_ideas}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <Space>
                          <Tag>{item.from_domain}</Tag>
                          <Text>→</Text>
                          <Tag>{item.to_domain}</Tag>
                          <Tag color={FEASIBILITY_COLORS[item.feasibility] || "default"}>
                            可行性: {item.feasibility}
                          </Tag>
                        </Space>
                      }
                      description={item.idea}
                    />
                  </List.Item>
                )}
              />
              <Divider />
            </>
          )}

          {/* 缺失环节 */}
          {deriveResult.missing_links && deriveResult.missing_links.length > 0 && (
            <>
              <Title level={5}>🔗 缺失环节</Title>
              {deriveResult.missing_links.map((link, i) => (
                <Alert
                  key={i}
                  type="warning"
                  showIcon
                  message={link.description}
                  description={`潜在价值: ${link.potential_value}`}
                  style={{ marginBottom: 8 }}
                />
              ))}
              <Divider />
            </>
          )}

          {/* 新假设 */}
          {deriveResult.new_hypotheses && deriveResult.new_hypotheses.length > 0 && (
            <>
              <Title level={5}>🔬 新研究假设</Title>
              {deriveResult.new_hypotheses.map((h, i) => (
                <Card
                  key={i}
                  size="small"
                  style={{ marginBottom: 8 }}
                  title={
                    <Space>
                      <Tag color={FEASIBILITY_COLORS[h.impact] || "default"}>
                        影响: {h.impact}
                      </Tag>
                      假设 {i + 1}
                    </Space>
                  }
                >
                  <Paragraph>{h.hypothesis}</Paragraph>
                  <Text type="secondary">验证方法: {h.evidence_needed}</Text>
                </Card>
              ))}
            </>
          )}
        </Card>
      )}

      {/* 无结果提示 */}
      {!discovering && !deriving && discoveries.length === 0 && !deriveResult && (
        <Alert
          message="点击「发现跨域关联」开始"
          description="AI 将分析知识库中的 65+ 个节点（40个知识节点 + 25篇论文），寻找跨领域的深层联系。需要配置 LLM API Key。"
          type="info"
          showIcon
        />
      )}
    </div>
  );
}
