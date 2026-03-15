import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import { Layout, Menu, theme, ConfigProvider } from "antd";
import {
  NodeIndexOutlined,
  FileTextOutlined,
  CloudDownloadOutlined,
  BulbOutlined,
  RobotOutlined,
} from "@ant-design/icons";
import GraphPage from "./pages/GraphPage";
import PapersPage from "./pages/PapersPage";
import CrawlerPage from "./pages/CrawlerPage";
import KnowledgeNodesPage from "./pages/KnowledgeNodesPage";
import AIDiscoveryPage from "./pages/AIDiscoveryPage";

const { Header, Sider, Content } = Layout;

const MENU_ITEMS = [
  { key: "/", icon: <NodeIndexOutlined />, label: <Link to="/">知识图谱</Link> },
  {
    key: "/ai",
    icon: <RobotOutlined />,
    label: <Link to="/ai">AI 发现</Link>,
  },
  {
    key: "/knowledge",
    icon: <BulbOutlined />,
    label: <Link to="/knowledge">知识节点</Link>,
  },
  {
    key: "/papers",
    icon: <FileTextOutlined />,
    label: <Link to="/papers">论文库</Link>,
  },
  {
    key: "/crawler",
    icon: <CloudDownloadOutlined />,
    label: <Link to="/crawler">论文爬取</Link>,
  },
];

function AppLayout() {
  const location = useLocation();
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={200} theme="light" style={{ borderRight: "1px solid #f0f0f0" }}>
        <div
          style={{
            height: 48,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 16,
            color: "#1677ff",
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          🧠 Knowledge Nexus
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={MENU_ITEMS}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: colorBgContainer,
            padding: "0 24px",
            borderBottom: "1px solid #f0f0f0",
            display: "flex",
            alignItems: "center",
            height: 48,
          }}
        >
          <h3 style={{ margin: 0, color: "#333" }}>
            跨领域知识关联引擎
          </h3>
        </Header>
        <Content
          style={{
            background: colorBgContainer,
            position: "relative",
            height: "calc(100vh - 48px)",
            overflow: "auto",
          }}
        >
          <Routes>
            <Route path="/" element={<GraphPage />} />
            <Route path="/ai" element={<AIDiscoveryPage />} />
            <Route path="/knowledge" element={<KnowledgeNodesPage />} />
            <Route path="/papers" element={<PapersPage />} />
            <Route path="/crawler" element={<CrawlerPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default function App() {
  return (
    <ConfigProvider
      theme={{
        token: { borderRadius: 6 },
      }}
    >
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </ConfigProvider>
  );
}
