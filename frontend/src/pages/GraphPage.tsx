import { useEffect, useRef, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import type { Core, EventObject } from "cytoscape";
import { Card, Empty, Select, Spin } from "antd";
import { useStore } from "../stores";

const LAYOUT_OPTIONS = [
  { value: "cose", label: "Force-Directed (Cose)" },
  { value: "circle", label: "Circle" },
  { value: "concentric", label: "Concentric" },
  { value: "breadthfirst", label: "Hierarchical" },
  { value: "grid", label: "Grid" },
];

export default function KnowledgeGraph() {
  const { graphNodes, graphEdges, graphLoading, papers, fetchSubgraph } =
    useStore();
  const cyRef = useRef<Core | null>(null);
  const [layout, setLayout] = useState("cose");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // 当有论文时，自动加载第一篇的子图
  useEffect(() => {
    if (papers.length > 0 && graphNodes.length === 0) {
      fetchSubgraph(papers[0].id);
    }
  }, [papers, graphNodes.length, fetchSubgraph]);

  // 转换为 Cytoscape 格式
  const elements = [
    ...graphNodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label.length > 40 ? n.label.slice(0, 37) + "..." : n.label,
        fullLabel: n.label,
        type: n.type,
        ...n.properties,
      },
    })),
    ...graphEdges.map((e) => ({
      data: {
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.type,
        type: e.type,
        ...e.properties,
      },
    })),
  ];

  const stylesheet: cytoscape.StylesheetStyle[] = [
    {
      selector: "node",
      style: {
        label: "data(label)",
        "background-color": "#1677ff",
        color: "#333",
        "font-size": "11px",
        "text-wrap": "wrap" as const,
        "text-max-width": "120px",
        "text-valign": "bottom" as const,
        "text-margin-y": 5,
        width: 30,
        height: 30,
      },
    },
    {
      selector: "node:selected",
      style: {
        "border-width": 3,
        "border-color": "#ff4d4f",
      },
    },
    {
      selector: "edge",
      style: {
        width: 2,
        "line-color": "#ccc",
        "target-arrow-color": "#ccc",
        "target-arrow-shape": "triangle" as const,
        "curve-style": "bezier" as const,
        label: "data(label)",
        "font-size": "9px",
        color: "#999",
        "text-rotation": "autorotate" as const,
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

  if (elements.length === 0) {
    return (
      <Empty
        description="暂无图谱数据。请先添加论文并建立关联。"
        style={{ padding: 80 }}
      />
    );
  }

  return (
    <div style={{ height: "100%" }}>
      <div
        style={{
          padding: "8px 16px",
          display: "flex",
          alignItems: "center",
          gap: 12,
          borderBottom: "1px solid #f0f0f0",
        }}
      >
        <span style={{ fontWeight: 500 }}>布局：</span>
        <Select
          value={layout}
          onChange={(val) => {
            setLayout(val);
            cyRef.current?.layout({ name: val, animate: true } as cytoscape.LayoutOptions).run();
          }}
          options={LAYOUT_OPTIONS}
          size="small"
          style={{ width: 180 }}
        />
        <span style={{ color: "#999", marginLeft: "auto" }}>
          {graphNodes.length} 节点 · {graphEdges.length} 边
        </span>
      </div>

      <CytoscapeComponent
        elements={elements}
        stylesheet={stylesheet}
        layout={{ name: layout } as cytoscape.LayoutOptions}
        style={{ width: "100%", height: "calc(100% - 45px)" }}
        cy={(cy: Core) => {
          cyRef.current = cy;
          cy.on("tap", "node", (evt: EventObject) => {
            const nodeId = evt.target.id();
            setSelectedNode(nodeId);
          });
          cy.on("dbltap", "node", (evt: EventObject) => {
            const nodeId = evt.target.id();
            fetchSubgraph(nodeId);
          });
        }}
      />

      {selectedNode && (
        <Card
          size="small"
          title="节点详情"
          style={{
            position: "absolute",
            bottom: 16,
            right: 16,
            width: 320,
            maxHeight: 200,
            overflow: "auto",
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          }}
          extra={
            <a onClick={() => setSelectedNode(null)}>关闭</a>
          }
        >
          {(() => {
            const node = graphNodes.find((n) => n.id === selectedNode);
            if (!node) return null;
            return (
              <div>
                <p style={{ fontWeight: 500 }}>{node.label}</p>
                <p style={{ color: "#666", fontSize: 12 }}>
                  类型: {node.type} | ID: {node.id}
                </p>
              </div>
            );
          })()}
        </Card>
      )}
    </div>
  );
}
