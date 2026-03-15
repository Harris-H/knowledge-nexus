import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import type { Core, EventObject } from "cytoscape";
import {
  Card, Empty, Select, Slider, Spin, Tag, Space, Typography, Input,
  Switch, AutoComplete, Tooltip,
} from "antd";
import { SearchOutlined, AimOutlined } from "@ant-design/icons";
import { useStore } from "../stores";

const { Text } = Typography;

const LAYOUT_OPTIONS = [
  { value: "cose", label: "力导向布局 (Cose)" },
  { value: "circle", label: "环形布局" },
  { value: "concentric", label: "同心圆布局" },
  { value: "breadthfirst", label: "层级布局" },
  { value: "grid", label: "网格布局" },
];

const RELATION_COLORS: Record<string, string> = {
  CITES: "#a0a0a0",
  IMPROVES: "#52c41a",
  INSPIRED_BY: "#faad14",
  INSPIRES: "#fa8c16",
  ANALOGOUS_TO: "#1677ff",
  BUILDS_ON: "#722ed1",
  RELATED_TO: "#13c2c2",
  PART_OF: "#389e0d",
  ENABLES: "#ff7a45",
  CONTRADICTS: "#ff4d4f",
  COMPETES_WITH: "#eb2f96",
  USED_BY: "#597ef7",
  REVIEWS: "#9254de",
};

const RELATION_LABELS: Record<string, string> = {
  CITES: "引用",
  IMPROVES: "改进",
  INSPIRED_BY: "受启发",
  INSPIRES: "启发了",
  ANALOGOUS_TO: "类比",
  BUILDS_ON: "基于",
  RELATED_TO: "相关",
  PART_OF: "组成",
  ENABLES: "促成",
  CONTRADICTS: "矛盾",
  COMPETES_WITH: "竞争",
  USED_BY: "被使用",
  REVIEWS: "综述",
};

const NODE_TYPE_COLORS: Record<string, string> = {
  paper: "#1677ff",
  phenomenon: "#52c41a",
  theorem: "#faad14",
  law: "#ff4d4f",
  method: "#722ed1",
  concept: "#13c2c2",
  principle: "#eb2f96",
  process: "#fa8c16",
  structure: "#597ef7",
};

const NODE_TYPE_LABELS: Record<string, string> = {
  paper: "📄 论文",
  phenomenon: "🌿 现象",
  theorem: "📐 定理",
  law: "⚖️ 定律",
  method: "🔧 方法",
  concept: "💡 概念",
  principle: "🎯 原理",
  process: "🔄 过程",
  structure: "🏗️ 结构",
};

// 领域颜色和标签
const DOMAIN_COLORS: Record<string, string> = {
  computer_science: "#722ed1",
  speech_ai: "#ff7a45",
  biology: "#52c41a",
  physics: "#1677ff",
  mathematics: "#faad14",
  neuroscience: "#eb2f96",
  chemistry: "#fa8c16",
  engineering: "#597ef7",
  psychology: "#9254de",
  ecology: "#389e0d",
  philosophy: "#13c2c2",
  sociology: "#cf1322",
  economics: "#d4b106",
  military_science: "#c41d7f",
  history: "#8c6e3a",
  art: "#f759ab",
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
  military_science: "⚔️ 军事学",
  history: "📜 历史",
  art: "🎨 艺术",
};

const CITATION_MARKS: Record<number, string> = {
  0: "全部",
  5000: "5K",
  10000: "1万",
  20000: "2万",
  50000: "5万",
};

export default function KnowledgeGraph() {
  const { graphNodes, graphEdges, graphLoading, fetchFullGraph, fetchSubgraph } =
    useStore();
  const cyRef = useRef<Core | null>(null);
  const [layout, setLayout] = useState("cose");
  const [minCitations, setMinCitations] = useState(0);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [searchText, setSearchText] = useState("");
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);
  const [crossDomainOnly, setCrossDomainOnly] = useState(false);

  const loadGraph = useCallback(() => {
    fetchFullGraph(minCitations);
  }, [fetchFullGraph, minCitations]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  // 提取所有出现的领域
  const allDomains = useMemo(() => {
    const domains = new Set<string>();
    graphNodes.forEach((n) => {
      const d = (n.properties?.domain as string) || "";
      if (d) domains.add(d);
    });
    return Array.from(domains).sort();
  }, [graphNodes]);

  // 获取节点的领域
  const getNodeDomain = (n: typeof graphNodes[0]): string => {
    return (n.properties?.domain as string) || "computer_science";
  };

  // 领域过滤后的节点和边
  const filteredData = useMemo(() => {
    let nodes = graphNodes;
    if (selectedDomains.length > 0) {
      nodes = graphNodes.filter((n) => selectedDomains.includes(getNodeDomain(n)));
    }
    const nodeIds = new Set(nodes.map((n) => n.id));

    let edges = graphEdges.filter(
      (e) => nodeIds.has(e.source) && nodeIds.has(e.target)
    );

    if (crossDomainOnly) {
      edges = edges.filter((e) => {
        const srcNode = nodes.find((n) => n.id === e.source);
        const tgtNode = nodes.find((n) => n.id === e.target);
        if (!srcNode || !tgtNode) return false;
        return getNodeDomain(srcNode) !== getNodeDomain(tgtNode);
      });
      // 只保留有跨域边的节点
      const connectedIds = new Set<string>();
      edges.forEach((e) => { connectedIds.add(e.source); connectedIds.add(e.target); });
      nodes = nodes.filter((n) => connectedIds.has(n.id));
    }

    return { nodes, edges };
  }, [graphNodes, graphEdges, selectedDomains, crossDomainOnly]);

  // 搜索补全选项
  const searchOptions = useMemo(() => {
    return graphNodes
      .map((n) => ({
        value: n.id,
        label: `${NODE_TYPE_LABELS[n.type] || n.type} ${n.label}`,
        nodeLabel: n.label || "",
      }))
      .filter((opt) =>
        searchText
          ? opt.nodeLabel.toLowerCase().includes(searchText.toLowerCase()) ||
            opt.label.toLowerCase().includes(searchText.toLowerCase())
          : true
      )
      .slice(0, 15);
  }, [graphNodes, searchText]);

  // 搜索选中→聚焦节点
  const handleSearchSelect = (nodeId: string) => {
    const cy = cyRef.current;
    if (!cy) return;
    const node = cy.getElementById(nodeId);
    if (node.length === 0) return;

    // 先清除之前的高亮
    cy.elements().removeClass("dimmed hover searched");

    // 高亮选中节点和邻居
    const neighborhood = node.closedNeighborhood();
    cy.elements().addClass("dimmed");
    neighborhood.removeClass("dimmed");
    node.addClass("searched");
    neighborhood.edges().addClass("hover");

    // 缩放到节点
    cy.animate({
      fit: { eles: neighborhood, padding: 80 },
      duration: 600,
    });

    setSelectedNode(nodeId);
    setSearchText("");
  };

  // 节点大小
  const getNodeSize = (node: { type: string; properties?: Record<string, unknown> }) => {
    if (node.type !== "paper") return 32;
    const citations = (node.properties?.citations as number) || 0;
    if (citations >= 30000) return 55;
    if (citations >= 15000) return 45;
    if (citations >= 5000) return 35;
    return 28;
  };

  const getNodeShape = (type: string) => {
    return type === "paper" ? "ellipse" : "diamond";
  };

  // 转换为 Cytoscape 格式
  const elements = [
    ...filteredData.nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label || "",
        fullTitle: (n.properties?.full_title as string) || n.label || "",
        type: n.type,
        citations: (n.properties?.citations as number) || 0,
        year: (n.properties?.year as number) || 0,
        venue: (n.properties?.venue as string) || "",
        domain: (n.properties?.domain as string) || "",
        summary: (n.properties?.summary as string) || "",
        nodeType: n.type,
        nodeSize: getNodeSize(n),
        nodeColor: NODE_TYPE_COLORS[n.type] || "#1677ff",
        nodeShape: getNodeShape(n.type),
      },
    })),
    ...filteredData.edges.map((e) => ({
      data: {
        id: e.id,
        source: e.source,
        target: e.target,
        label: RELATION_LABELS[e.type] || e.type.replace(/_/g, " "),
        type: e.type,
        description: (e.properties?.description as string) || "",
        lineColor: RELATION_COLORS[e.type] || "#ccc",
      },
    })),
  ];

  const stylesheet: cytoscape.StylesheetStyle[] = [
    {
      selector: "node",
      style: {
        label: "data(label)",
        "background-color": "data(nodeColor)",
        "background-opacity": 0.9,
        shape: "data(nodeShape)" as unknown as cytoscape.Css.NodeShape,
        color: "#222",
        "font-size": "10px",
        "font-weight": "bold" as const,
        "text-wrap": "wrap" as const,
        "text-max-width": "150px",
        "text-valign": "bottom" as const,
        "text-margin-y": 8,
        width: "data(nodeSize)",
        height: "data(nodeSize)",
        "border-width": 2,
        "border-color": "#e6f4ff",
        "overlay-opacity": 0,
        "transition-property":
          "background-color border-color border-width" as const,
        "transition-duration": "0.2s" as unknown as number,
      },
    },
    {
      selector: "node:selected",
      style: {
        "border-width": 4,
        "border-color": "#ff4d4f",
        "background-color": "#ff7a45",
        "font-size": "12px",
        "z-index": 999,
      },
    },
    {
      selector: "node.hover",
      style: {
        "border-width": 3,
        "border-color": "#faad14",
        "background-color": "#1890ff",
        "z-index": 998,
      },
    },
    {
      selector: "node.searched",
      style: {
        "border-width": 5,
        "border-color": "#ff4d4f",
        "background-opacity": 1,
        "font-size": "13px",
        "z-index": 999,
      },
    },
    {
      selector: "node.dimmed",
      style: {
        "background-opacity": 0.15,
        "text-opacity": 0.2,
        "border-opacity": 0.1,
      },
    },
    {
      selector: "edge",
      style: {
        width: 2.5,
        "line-color": "data(lineColor)",
        "target-arrow-color": "data(lineColor)",
        "target-arrow-shape": "triangle" as const,
        "curve-style": "bezier" as const,
        label: "data(label)",
        "font-size": "12px",
        "font-weight": "bold" as const,
        color: "#1a1a1a",
        "text-rotation": "autorotate" as const,
        "text-margin-y": -12,
        opacity: 0.85,
        "text-background-color": "#fffbe6",
        "text-background-opacity": 0.95,
        "text-background-padding": "4px" as unknown as string,
        "text-background-shape": "roundrectangle" as const,
      },
    },
    {
      selector: "edge:selected",
      style: { width: 4, opacity: 1 },
    },
    {
      selector: "edge.hover",
      style: {
        width: 4,
        opacity: 1,
        "font-size": "13px",
        color: "#000",
        "text-background-color": "#ffec3d",
        "text-background-opacity": 1,
      },
    },
    {
      selector: "edge.dimmed",
      style: { opacity: 0.08, "text-opacity": 0.1 },
    },
  ];

  if (graphLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" tip="加载图谱..." />
      </div>
    );
  }

  return (
    <div style={{ height: "100%", position: "relative" }}>
      {/* 工具栏 */}
      <div
        style={{
          padding: "8px 16px",
          display: "flex",
          alignItems: "center",
          gap: 12,
          borderBottom: "1px solid #f0f0f0",
          background: "#fafafa",
          flexWrap: "wrap",
        }}
      >
        {/* 搜索 */}
        <AutoComplete
          options={searchOptions}
          onSearch={setSearchText}
          onSelect={handleSearchSelect}
          value={searchText}
          placeholder="搜索节点..."
          style={{ width: 200 }}
          size="small"
          allowClear
          suffixIcon={<SearchOutlined />}
        />

        {/* 领域过滤 */}
        <Select
          mode="multiple"
          placeholder="筛选领域"
          value={selectedDomains}
          onChange={setSelectedDomains}
          style={{ minWidth: 180, maxWidth: 400 }}
          size="small"
          maxTagCount={2}
          allowClear
          options={allDomains.map((d) => ({
            value: d,
            label: DOMAIN_LABELS[d] || d,
          }))}
        />

        {/* 跨域模式 */}
        <Tooltip title="只显示跨越不同领域的关联边">
          <Space size={4}>
            <Switch
              size="small"
              checked={crossDomainOnly}
              onChange={setCrossDomainOnly}
            />
            <Text style={{ fontSize: 12 }}>跨域</Text>
          </Space>
        </Tooltip>

        {/* 布局 */}
        <Select
          value={layout}
          onChange={(val) => {
            setLayout(val);
            cyRef.current
              ?.layout({ name: val, animate: true, padding: 60 } as cytoscape.LayoutOptions)
              .run();
          }}
          options={LAYOUT_OPTIONS}
          size="small"
          style={{ width: 140 }}
        />

        {/* 引用过滤 */}
        <Space style={{ minWidth: 200 }}>
          <Text style={{ fontSize: 12 }}>引用≥</Text>
          <div style={{ width: 180 }}>
            <Slider
              min={0}
              max={50000}
              step={1000}
              value={minCitations}
              onChange={setMinCitations}
              onChangeComplete={loadGraph}
              marks={CITATION_MARKS}
              tooltip={{
                formatter: (v) => (v ? `≥ ${v.toLocaleString()}` : "全部"),
              }}
            />
          </div>
        </Space>

        <Text type="secondary" style={{ marginLeft: "auto", fontSize: 12 }}>
          {filteredData.nodes.filter((n) => n.type === "paper").length} 论文
          {" · "}
          {filteredData.nodes.filter((n) => n.type !== "paper").length} 知识
          {" · "}
          {filteredData.edges.length} 关系
        </Text>
      </div>

      {/* 图谱区域 */}
      {elements.length === 0 ? (
        <Empty
          description="无符合条件的节点。请调整过滤条件。"
          style={{ padding: 80 }}
        />
      ) : (
        <CytoscapeComponent
          elements={elements}
          stylesheet={stylesheet}
          layout={
            {
              name: layout,
              animate: true,
              animationDuration: 500,
              padding: 80,
              nodeRepulsion: () => 50000,
              idealEdgeLength: () => 300,
              edgeElasticity: () => 80,
              gravity: 0.08,
              numIter: 3000,
              nodeDimensionsIncludeLabels: true,
            } as cytoscape.LayoutOptions
          }
          style={{ width: "100%", height: "calc(100% - 72px)" }}
          cy={(cy: Core) => {
            cyRef.current = cy;

            cy.on("tap", "node", (evt: EventObject) => {
              setSelectedNode(evt.target.id());
            });
            cy.on("tap", (evt: EventObject) => {
              if (evt.target === cy) {
                setSelectedNode(null);
                cy.elements().removeClass("dimmed hover searched");
              }
            });
            cy.on("dbltap", "node", (evt: EventObject) => {
              fetchSubgraph(evt.target.id());
            });

            cy.on("mouseover", "node", (evt: EventObject) => {
              const node = evt.target;
              const neighborhood = node.closedNeighborhood();
              cy.elements().addClass("dimmed");
              neighborhood.removeClass("dimmed");
              node.addClass("hover");
              neighborhood.edges().addClass("hover");
            });
            cy.on("mouseout", "node", () => {
              cy.elements().removeClass("dimmed hover");
            });

            cy.on("mouseover", "edge", (evt: EventObject) => {
              const edge = evt.target;
              edge.addClass("hover");
              const desc = edge.data("description");
              if (desc) {
                edge.style("label", desc.length > 40 ? desc.slice(0, 38) + "..." : desc);
              }
            });
            cy.on("mouseout", "edge", (evt: EventObject) => {
              const edge = evt.target;
              edge.removeClass("hover");
              edge.style("label", edge.data("label"));
            });
          }}
        />
      )}

      {/* 图例 — 按领域展示 */}
      <div
        style={{
          position: "absolute",
          top: 52,
          left: 16,
          background: "rgba(255,255,255,0.95)",
          padding: "8px 12px",
          borderRadius: 6,
          boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
          fontSize: 11,
          maxHeight: "calc(100% - 140px)",
          overflowY: "auto",
          minWidth: 130,
        }}
      >
        <Text strong style={{ display: "block", marginBottom: 4, fontSize: 12 }}>
          节点类型
        </Text>
        {Object.entries(NODE_TYPE_COLORS).map(([type, color]) => (
          <div key={type} style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 2 }}>
            <div
              style={{
                width: 9,
                height: 9,
                background: color,
                borderRadius: type === "paper" ? "50%" : 2,
                transform: type === "paper" ? "none" : "rotate(45deg)",
                flexShrink: 0,
              }}
            />
            <span>{NODE_TYPE_LABELS[type] || type}</span>
          </div>
        ))}
        <div style={{ borderTop: "1px solid #f0f0f0", margin: "4px 0" }} />
        <Text strong style={{ display: "block", marginBottom: 4, fontSize: 12 }}>
          关系
        </Text>
        {Object.entries(RELATION_COLORS).map(([type, color]) => (
          <div key={type} style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 1 }}>
            <div style={{ width: 16, height: 2.5, background: color, borderRadius: 2, flexShrink: 0 }} />
            <span>{RELATION_LABELS[type] || type}</span>
          </div>
        ))}
      </div>

      {/* 节点详情面板 */}
      {selectedNode && (() => {
        const node = graphNodes.find((n) => n.id === selectedNode);
        if (!node) return null;
        const isPaper = node.type === "paper";
        const citations = (node.properties?.citations as number) || 0;
        const year = (node.properties?.year as number) || 0;
        const venue = (node.properties?.venue as string) || "";
        const fullTitle = (node.properties?.full_title as string) || node.label || "";
        const domain = (node.properties?.domain as string) || "";
        const summary = (node.properties?.summary as string) || "";
        const description = (node.properties?.description as string) || "";
        const nodeType = node.type;
        const connectedEdges = graphEdges.filter(
          (e) => e.source === selectedNode || e.target === selectedNode
        );

        return (
          <Card
            size="small"
            title={
              <Space>
                <Tag color={NODE_TYPE_COLORS[nodeType] || "#1677ff"}>
                  {NODE_TYPE_LABELS[nodeType] || nodeType}
                </Tag>
                <span style={{ fontSize: 13 }}>{node.label}</span>
              </Space>
            }
            style={{
              position: "absolute",
              bottom: 16,
              right: 16,
              width: 380,
              maxHeight: 400,
              overflow: "auto",
              boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
              borderRadius: 8,
            }}
            extra={<a onClick={() => setSelectedNode(null)}>关闭</a>}
          >
            {isPaper && fullTitle !== node.label && (
              <p style={{ fontSize: 12, color: "#666", marginBottom: 8 }}>{fullTitle}</p>
            )}
            {!isPaper && (summary || description) && (
              <p style={{ fontSize: 12, color: "#555", marginBottom: 8 }}>
                {summary || (description.length > 100 ? description.slice(0, 100) + "..." : description)}
              </p>
            )}
            <Space wrap style={{ marginBottom: 8 }}>
              {year > 0 && <Tag>{year}</Tag>}
              {isPaper && <Tag color="blue">{citations.toLocaleString()} 引用</Tag>}
              {venue && <Tag color="green">{venue}</Tag>}
              {domain && <Tag color={DOMAIN_COLORS[domain] || "orange"}>{DOMAIN_LABELS[domain] || domain}</Tag>}
            </Space>
            {connectedEdges.length > 0 && (
              <>
                <Text strong style={{ display: "block", marginBottom: 4, fontSize: 12 }}>
                  关联 ({connectedEdges.length}):
                </Text>
                {connectedEdges.map((edge) => {
                  const otherId = edge.source === selectedNode ? edge.target : edge.source;
                  const otherNode = graphNodes.find((n) => n.id === otherId);
                  const direction = edge.source === selectedNode ? "→" : "←";
                  const desc = (edge.properties?.description as string) || "";
                  return (
                    <div
                      key={edge.id}
                      style={{
                        fontSize: 11,
                        color: "#555",
                        marginBottom: 5,
                        padding: "3px 0",
                        borderBottom: "1px dashed #f0f0f0",
                      }}
                    >
                      <div>
                        <Tag color={RELATION_COLORS[edge.type] || "#ccc"} style={{ fontSize: 10 }}>
                          {RELATION_LABELS[edge.type] || edge.type}
                        </Tag>
                        {direction}{" "}
                        <a onClick={() => { setSelectedNode(otherId); handleSearchSelect(otherId); }}>
                          {otherNode ? (otherNode.label || "").slice(0, 35) : otherId}
                        </a>
                      </div>
                      {desc && (
                        <div style={{ fontSize: 10, color: "#999", marginTop: 2, paddingLeft: 8 }}>
                          💡 {desc}
                        </div>
                      )}
                    </div>
                  );
                })}
              </>
            )}
          </Card>
        );
      })()}
    </div>
  );
}
