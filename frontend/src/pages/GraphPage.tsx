import { useEffect, useRef, useState, useCallback } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import type { Core, EventObject } from "cytoscape";
import { Card, Empty, Select, Slider, Spin, Tag, Space, Typography } from "antd";
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
  ANALOGOUS_TO: "#1677ff",
  BUILDS_ON: "#722ed1",
  RELATED_TO: "#13c2c2",
  CONTRADICTS: "#ff4d4f",
  COMPETES_WITH: "#eb2f96",
  USED_BY: "#597ef7",
};

const RELATION_LABELS: Record<string, string> = {
  CITES: "引用",
  IMPROVES: "改进",
  INSPIRED_BY: "受启发",
  ANALOGOUS_TO: "类比",
  BUILDS_ON: "基于",
  RELATED_TO: "相关",
  CONTRADICTS: "矛盾",
  COMPETES_WITH: "竞争",
  USED_BY: "被使用",
};

const CITATION_MARKS: Record<number, string> = {
  0: "全部",
  1000: "1K",
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
  const [minCitations, setMinCitations] = useState(10000);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const loadGraph = useCallback(() => {
    fetchFullGraph(minCitations);
  }, [fetchFullGraph, minCitations]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  // 节点大小根据引用量缩放
  const getNodeSize = (citations: number) => {
    if (citations >= 30000) return 55;
    if (citations >= 15000) return 45;
    if (citations >= 5000) return 35;
    return 28;
  };

  // 转换为 Cytoscape 格式
  const elements = [
    ...graphNodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label || "",
        fullTitle: (n.properties?.full_title as string) || n.label || "",
        type: n.type,
        citations: (n.properties?.citations as number) || 0,
        year: (n.properties?.year as number) || 0,
        venue: (n.properties?.venue as string) || "",
        nodeSize: getNodeSize((n.properties?.citations as number) || 0),
      },
    })),
    ...graphEdges.map((e) => ({
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
        "background-color": "#1677ff",
        "background-opacity": 0.9,
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
      selector: "node.dimmed",
      style: {
        "background-opacity": 0.25,
        "text-opacity": 0.3,
        "border-opacity": 0.2,
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
        "font-size": "11px",
        color: "#555",
        "text-rotation": "autorotate" as const,
        "text-margin-y": -12,
        opacity: 0.75,
        "text-background-color": "#fff",
        "text-background-opacity": 0.8,
      },
    },
    {
      selector: "edge:selected",
      style: {
        width: 4,
        opacity: 1,
      },
    },
    {
      selector: "edge.hover",
      style: {
        width: 3.5,
        opacity: 1,
      },
    },
    {
      selector: "edge.dimmed",
      style: {
        opacity: 0.12,
      },
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
          padding: "10px 16px",
          display: "flex",
          alignItems: "center",
          gap: 16,
          borderBottom: "1px solid #f0f0f0",
          background: "#fafafa",
          flexWrap: "wrap",
        }}
      >
        <Space>
          <Text strong>布局：</Text>
          <Select
            value={layout}
            onChange={(val) => {
              setLayout(val);
              cyRef.current
                ?.layout({ name: val, animate: true } as cytoscape.LayoutOptions)
                .run();
            }}
            options={LAYOUT_OPTIONS}
            size="small"
            style={{ width: 160 }}
          />
        </Space>

        <Space style={{ flex: 1, minWidth: 280 }}>
          <Text strong>引用过滤：</Text>
          <div style={{ width: 300 }}>
            <Slider
              min={0}
              max={50000}
              step={1000}
              value={minCitations}
              onChange={setMinCitations}
              onChangeComplete={loadGraph}
              marks={CITATION_MARKS}
              tooltip={{
                formatter: (v) => (v ? `≥ ${v.toLocaleString()} 引用` : "全部"),
              }}
            />
          </div>
        </Space>

        <Text type="secondary" style={{ marginLeft: "auto" }}>
          {graphNodes.length} 节点 · {graphEdges.length} 边
        </Text>
      </div>

      {/* 图谱区域 */}
      {elements.length === 0 ? (
        <Empty
          description="暂无符合条件的论文。请降低引用量阈值或先爬取数据。"
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
              padding: 60,
              nodeRepulsion: () => 30000,
              idealEdgeLength: () => 250,
              edgeElasticity: () => 100,
              gravity: 0.15,
              numIter: 2000,
              nodeDimensionsIncludeLabels: true,
            } as cytoscape.LayoutOptions
          }
          style={{ width: "100%", height: "calc(100% - 80px)" }}
          cy={(cy: Core) => {
            cyRef.current = cy;

            // 点击节点
            cy.on("tap", "node", (evt: EventObject) => {
              setSelectedNode(evt.target.id());
            });
            cy.on("tap", (evt: EventObject) => {
              if (evt.target === cy) {
                setSelectedNode(null);
                // 清除所有高亮
                cy.elements().removeClass("dimmed hover");
              }
            });
            cy.on("dbltap", "node", (evt: EventObject) => {
              fetchSubgraph(evt.target.id());
            });

            // 鼠标悬停高亮
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

            // 边悬停显示描述
            cy.on("mouseover", "edge", (evt: EventObject) => {
              const edge = evt.target;
              edge.addClass("hover");
              const desc = edge.data("description");
              if (desc) {
                edge.style("label", desc.length > 30 ? desc.slice(0, 28) + "..." : desc);
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

      {/* 图例 */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 16,
          background: "rgba(255,255,255,0.92)",
          padding: "8px 12px",
          borderRadius: 6,
          boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
          fontSize: 12,
        }}
      >
        <Text strong style={{ display: "block", marginBottom: 4 }}>
          关系类型
        </Text>
        {Object.entries(RELATION_COLORS).map(([type, color]) => (
          <div key={type} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
            <div
              style={{
                width: 20,
                height: 3,
                background: color,
                borderRadius: 2,
              }}
            />
            <span>{RELATION_LABELS[type] || type}</span>
          </div>
        ))}
      </div>

      {/* 节点详情面板 */}
      {selectedNode && (() => {
        const node = graphNodes.find((n) => n.id === selectedNode);
        if (!node) return null;
        const citations = (node.properties?.citations as number) || 0;
        const year = (node.properties?.year as number) || 0;
        const venue = (node.properties?.venue as string) || "";
        const fullTitle = (node.properties?.full_title as string) || node.label || "";
        const connectedEdges = graphEdges.filter(
          (e) => e.source === selectedNode || e.target === selectedNode
        );

        return (
          <Card
            size="small"
            title={node.label}
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
            {fullTitle !== node.label && (
              <p style={{ fontSize: 12, color: "#666", marginBottom: 8 }}>
                {fullTitle}
              </p>
            )}
            <Space wrap style={{ marginBottom: 8 }}>
              {year > 0 && <Tag>{year}</Tag>}
              <Tag color="blue">{citations.toLocaleString()} 引用</Tag>
              {venue && <Tag color="green">{venue}</Tag>}
            </Space>
            {connectedEdges.length > 0 && (
              <>
                <Text
                  strong
                  style={{ display: "block", marginBottom: 4, fontSize: 12 }}
                >
                  关联 ({connectedEdges.length}):
                </Text>
                {connectedEdges.map((edge) => {
                  const otherId =
                    edge.source === selectedNode ? edge.target : edge.source;
                  const otherNode = graphNodes.find((n) => n.id === otherId);
                  const direction = edge.source === selectedNode ? "→" : "←";
                  const desc = (edge.properties?.description as string) || "";
                  return (
                    <div
                      key={edge.id}
                      style={{
                        fontSize: 11,
                        color: "#555",
                        marginBottom: 6,
                        padding: "3px 0",
                        borderBottom: "1px dashed #f0f0f0",
                      }}
                    >
                      <div>
                        <Tag
                          color={RELATION_COLORS[edge.type] || "#ccc"}
                          style={{ fontSize: 10 }}
                        >
                          {RELATION_LABELS[edge.type] || edge.type}
                        </Tag>
                        {direction}{" "}
                        {otherNode
                          ? (otherNode.label || "").slice(0, 40)
                          : otherId}
                      </div>
                      {desc && (
                        <div
                          style={{
                            fontSize: 10,
                            color: "#999",
                            marginTop: 2,
                            paddingLeft: 8,
                          }}
                        >
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
