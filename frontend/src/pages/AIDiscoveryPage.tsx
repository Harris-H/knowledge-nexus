import { useState, useRef, useEffect, useCallback } from "react";
import {
  Card, Button, Space, Tag, Typography, Spin, message, Input,
  Alert, Divider, Progress, List, Tooltip,
} from "antd";
import {
  SendOutlined, RobotOutlined, UserOutlined, BulbOutlined,
  ClearOutlined, SearchOutlined, ExperimentOutlined,
  CopyOutlined, CheckOutlined, ReloadOutlined,
} from "@ant-design/icons";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { aiApi } from "../api";
import type { ChatMessage, ChatResponse } from "../api";

const { Text, Paragraph } = Typography;

interface DisplayMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  skill_used?: string;
  structured_data?: ChatResponse["structured_data"];
  loading?: boolean;
}

const SKILL_LABELS: Record<string, string> = {
  search_knowledge: "🔍 搜索知识",
  discover_relations: "⚡ 发现关联",
  analyze_pair: "🔬 配对分析",
  derive_knowledge: "🧠 推导知识",
  get_domain_digest: "📋 领域摘要",
  cross_domain_analysis: "🔗 跨域分析",
  list_domains: "📊 领域列表",
  general_chat: "💬 对话",
};

const SUGGESTIONS = [
  { icon: <SearchOutlined />, text: "有哪些知识领域？" },
  { icon: <ExperimentOutlined />, text: "分析计算机和生物学的跨域关联" },
  { icon: <BulbOutlined />, text: "在所有领域中发现新的跨域关联" },
];

let msgIdCounter = 0;
const nextMsgId = () => `msg-${++msgIdCounter}`;

export default function AIDiscoveryPage() {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [sending, setSending] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSend = async (text?: string) => {
    const content = (text || inputValue).trim();
    if (!content || sending) return;

    setInputValue("");
    const userMsg: DisplayMessage = { id: nextMsgId(), role: "user", content };
    const loadingMsg: DisplayMessage = { id: nextMsgId(), role: "assistant", content: "", loading: true };

    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    setSending(true);

    // Build chat history for API
    const apiMessages: ChatMessage[] = [
      ...messages.filter((m) => !m.loading).map((m) => ({ role: m.role, content: m.content })),
      { role: "user" as const, content },
    ];

    try {
      const res = await aiApi.chat(apiMessages);
      const assistantMsg: DisplayMessage = {
        id: loadingMsg.id,
        role: "assistant",
        content: res.data.content,
        skill_used: res.data.skill_used || undefined,
        structured_data: res.data.structured_data || undefined,
      };
      setMessages((prev) => prev.map((m) => (m.id === loadingMsg.id ? assistantMsg : m)));
    } catch (e: any) {
      const errText = e?.response?.data?.detail || e?.message || "请求失败";
      const errorMsg: DisplayMessage = {
        id: loadingMsg.id,
        role: "assistant",
        content: `❌ 抱歉，出现了错误: ${errText}`,
      };
      setMessages((prev) => prev.map((m) => (m.id === loadingMsg.id ? errorMsg : m)));
      message.error("请求失败");
    } finally {
      setSending(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
  };

  const handleCopy = async (msg: DisplayMessage) => {
    try {
      await navigator.clipboard.writeText(msg.content);
      setCopiedId(msg.id);
      message.success("已复制到剪贴板");
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      message.error("复制失败");
    }
  };

  const handleRetry = async (msg: DisplayMessage) => {
    if (sending) return;

    // Find the user message right before this assistant message
    const msgIndex = messages.findIndex((m) => m.id === msg.id);
    if (msgIndex < 1) return;

    let userMsgIndex = msgIndex - 1;
    while (userMsgIndex >= 0 && messages[userMsgIndex].role !== "user") {
      userMsgIndex--;
    }
    if (userMsgIndex < 0) return;

    const userContent = messages[userMsgIndex].content;

    // Keep messages up to (and including) the user message, discard the rest
    const kept = messages.slice(0, userMsgIndex + 1);
    const loadingMsg: DisplayMessage = { id: nextMsgId(), role: "assistant", content: "", loading: true };
    setMessages([...kept, loadingMsg]);
    setSending(true);

    const apiMessages: ChatMessage[] = kept
      .filter((m) => !m.loading)
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      const res = await aiApi.chat(apiMessages);
      const assistantMsg: DisplayMessage = {
        id: loadingMsg.id,
        role: "assistant",
        content: res.data.content,
        skill_used: res.data.skill_used || undefined,
        structured_data: res.data.structured_data || undefined,
      };
      setMessages((prev) => prev.map((m) => (m.id === loadingMsg.id ? assistantMsg : m)));
    } catch (e: any) {
      const errText = e?.response?.data?.detail || e?.message || "请求失败";
      const errorMsg: DisplayMessage = {
        id: loadingMsg.id,
        role: "assistant",
        content: `❌ 抱歉，出现了错误: ${errText}`,
      };
      setMessages((prev) => prev.map((m) => (m.id === loadingMsg.id ? errorMsg : m)));
      message.error("请求失败");
    } finally {
      setSending(false);
    }
  };

  const showWelcome = messages.length === 0;

  return (
    <div className="chat-container">
      {/* Messages area */}
      <div className="chat-messages">
        {showWelcome && (
          <div className="chat-welcome">
            <RobotOutlined style={{ fontSize: 48, color: "#1677ff", marginBottom: 16 }} />
            <h2 style={{ margin: "0 0 8px", color: "#333" }}>AI 知识发现助手</h2>
            <p style={{ color: "#888", marginBottom: 24 }}>
              我可以帮你搜索知识、发现跨域关联、分析领域摘要。试试下面的示例：
            </p>
            <Space direction="vertical" size={8}>
              {SUGGESTIONS.map((s, i) => (
                <Button
                  key={i}
                  icon={s.icon}
                  onClick={() => handleSend(s.text)}
                  className="chat-suggestion-btn"
                >
                  {s.text}
                </Button>
              ))}
            </Space>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-msg chat-msg-${msg.role}`}>
            <div className="chat-msg-avatar">
              {msg.role === "user" ? <UserOutlined /> : <RobotOutlined />}
            </div>
            <div className="chat-msg-body">
              {msg.loading ? (
                <div className="chat-thinking">
                  <Spin size="small" />
                  <span>思考中...</span>
                </div>
              ) : (
                <>
                  {msg.skill_used && msg.skill_used !== "general_chat" && (
                    <Tag color="blue" style={{ marginBottom: 6 }}>
                      {SKILL_LABELS[msg.skill_used] || msg.skill_used}
                    </Tag>
                  )}
                  <div className="chat-msg-content digest-markdown-content">
                    <Markdown remarkPlugins={[remarkGfm]}>{msg.content}</Markdown>
                  </div>
                  {msg.structured_data && (
                    <StructuredDataCard data={msg.structured_data} />
                  )}
                  {msg.role === "assistant" && (
                    <div className="chat-msg-actions">
                      <Tooltip title={copiedId === msg.id ? "已复制" : "复制"}>
                        <Button
                          type="text"
                          size="small"
                          icon={copiedId === msg.id ? <CheckOutlined /> : <CopyOutlined />}
                          onClick={() => handleCopy(msg)}
                          className={`chat-action-btn ${copiedId === msg.id ? "chat-action-btn-copied" : ""}`}
                        />
                      </Tooltip>
                      <Tooltip title="重新生成">
                        <Button
                          type="text"
                          size="small"
                          icon={<ReloadOutlined />}
                          onClick={() => handleRetry(msg)}
                          disabled={sending}
                          className="chat-action-btn"
                        />
                      </Tooltip>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="chat-input-area">
        <div className="chat-input-inner">
          {messages.length > 0 && (
            <Tooltip title="清空对话">
              <Button
                icon={<ClearOutlined />}
                onClick={handleClear}
                size="small"
                style={{ marginRight: 8 }}
              />
            </Tooltip>
          )}
          <Input
            ref={inputRef as any}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onPressEnter={() => handleSend()}
            placeholder="输入你的问题... 例如「分析物理和数学的跨域关联」"
            disabled={sending}
            size="large"
            style={{ flex: 1 }}
            suffix={
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={() => handleSend()}
                loading={sending}
                disabled={!inputValue.trim()}
              />
            }
          />
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
//  结构化数据卡片
// ══════════════════════════════════════════════════════════════

const FEASIBILITY_COLORS: Record<string, string> = {
  high: "green", medium: "gold", low: "red",
};

const RELATION_TYPE_COLORS: Record<string, string> = {
  INSPIRES: "orange", ANALOGOUS_TO: "blue", RELATED_TO: "cyan",
  BUILDS_ON: "purple", IMPROVES: "green", ENABLES: "volcano", PART_OF: "lime",
};

function StructuredDataCard({ data }: { data: { type: string; data: Record<string, unknown> } }) {
  const { type, data: payload } = data;

  if (type === "search_results") {
    const items = (payload.items as any[]) || [];
    if (!items.length) return null;
    return (
      <Card size="small" className="chat-result-card" title={`🔍 找到 ${items.length} 条结果`}>
        <List
          size="small"
          dataSource={items.slice(0, 8)}
          renderItem={(item: any) => (
            <List.Item>
              <List.Item.Meta
                title={<Space><Tag>{item.node_type}</Tag><Text strong>{item.name}</Text></Space>}
                description={item.summary?.slice(0, 100)}
              />
            </List.Item>
          )}
        />
      </Card>
    );
  }

  if (type === "discoveries") {
    const discoveries = (payload.discoveries as any[]) || [];
    if (!discoveries.length) return null;
    return (
      <Card size="small" className="chat-result-card" title={`⚡ ${discoveries.length} 条跨域关联`}>
        {discoveries.map((d: any, i: number) => (
          <div key={i} style={{ padding: "8px 0", borderBottom: i < discoveries.length - 1 ? "1px solid #f0f0f0" : "none" }}>
            <Space wrap>
              <Tag color={RELATION_TYPE_COLORS[d.relation_type] || "default"}>{d.relation_type}</Tag>
              <Text strong>{d.source_name}</Text>
              <Text type="secondary">→</Text>
              <Text strong>{d.target_name}</Text>
              <Progress type="circle" percent={Math.round(d.confidence * 100)} size={24} />
            </Space>
            <Paragraph style={{ margin: "4px 0 0", fontSize: 12, color: "#666" }}>{d.description}</Paragraph>
          </div>
        ))}
      </Card>
    );
  }

  if (type === "pair_analysis") {
    return (
      <Card size="small" className="chat-result-card" title="🔬 配对分析详情">
        <Space style={{ marginBottom: 8 }}>
          <Tag color={(payload as any).has_relation ? "green" : "red"}>
            {(payload as any).has_relation ? "✅ 存在关联" : "❌ 无明显关联"}
          </Tag>
          <Tag color={RELATION_TYPE_COLORS[(payload as any).relation_type] || "default"}>
            {(payload as any).relation_type}
          </Tag>
          <Progress type="circle" percent={Math.round(((payload as any).confidence || 0) * 100)} size={28} />
        </Space>
        {(payload as any).new_insight && (
          <Alert type="success" message={`💡 ${(payload as any).new_insight}`} style={{ marginTop: 8 }} />
        )}
      </Card>
    );
  }

  if (type === "derive_result") {
    const pattern = payload.abstract_pattern as any;
    const transfers = (payload.transfer_ideas as any[]) || [];
    const hypotheses = (payload.new_hypotheses as any[]) || [];
    return (
      <Card size="small" className="chat-result-card" title="🧠 知识推导详情">
        {pattern && (
          <Alert type="info" message={`🔮 ${pattern.name}`} description={pattern.description} style={{ marginBottom: 8 }} />
        )}
        {transfers.length > 0 && (
          <>
            <Divider orientation={"left" as any} style={{ fontSize: 12 }}>知识迁移</Divider>
            {transfers.map((t: any, i: number) => (
              <div key={i} style={{ marginBottom: 4 }}>
                <Space>
                  <Tag>{t.from_domain}</Tag><Text type="secondary">→</Text><Tag>{t.to_domain}</Tag>
                  <Tag color={FEASIBILITY_COLORS[t.feasibility]}>{t.feasibility}</Tag>
                </Space>
                <Paragraph style={{ fontSize: 12, margin: "2px 0 0" }}>{t.idea}</Paragraph>
              </div>
            ))}
          </>
        )}
        {hypotheses.length > 0 && (
          <>
            <Divider orientation={"left" as any} style={{ fontSize: 12 }}>新假设</Divider>
            {hypotheses.map((h: any, i: number) => (
              <div key={i} style={{ marginBottom: 4, fontSize: 12 }}>
                <Tag color={FEASIBILITY_COLORS[h.impact]}>影响: {h.impact}</Tag> {h.hypothesis}
              </div>
            ))}
          </>
        )}
      </Card>
    );
  }

  if (type === "cross_domain_analysis") {
    const analogies = (payload.analogies as any[]) || [];
    const transfers = (payload.transfer_ideas as any[]) || [];
    return (
      <Card size="small" className="chat-result-card" title="🔗 跨域分析详情">
        {(payload as any).summary && (
          <Alert type="success" message={(payload as any).summary} style={{ marginBottom: 8 }} />
        )}
        {analogies.length > 0 && (
          <>
            <Divider orientation={"left" as any} style={{ fontSize: 12 }}>结构类比</Divider>
            {analogies.map((a: any, i: number) => (
              <div key={i} style={{ marginBottom: 6 }}>
                <Space>
                  <Tag color="blue">{a.concept_a}</Tag>
                  <Text type="secondary">≈</Text>
                  <Tag color="purple">{a.concept_b}</Tag>
                  <Tag>{a.depth}</Tag>
                </Space>
                <Paragraph style={{ fontSize: 12, margin: "2px 0 0" }}>{a.description}</Paragraph>
              </div>
            ))}
          </>
        )}
        {transfers.length > 0 && (
          <>
            <Divider orientation={"left" as any} style={{ fontSize: 12 }}>知识迁移</Divider>
            {transfers.map((t: any, i: number) => (
              <div key={i} style={{ marginBottom: 4, fontSize: 12 }}>
                <Tag>{t.from_domain}</Tag> → <Tag>{t.to_domain}</Tag>
                <Tag color={FEASIBILITY_COLORS[t.feasibility]}>{t.feasibility}</Tag>
                <br />{t.idea}
              </div>
            ))}
          </>
        )}
      </Card>
    );
  }

  // domain_list 等由 Markdown content 已经渲染，无需额外卡片
  return null;
}
