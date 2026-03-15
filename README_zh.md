# Knowledge Nexus — 跨领域知识关联引擎

[English](README.md) | 中文

> 借助 AI 发现看似无关事物之间的深层关联，将孤立的知识点编织成互联互通的知识网络。

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 项目愿景

人类知识分散在不同领域中，但本质上许多概念跨域相通：

| 领域 A | ↔ | 领域 B |
|---|---|---|
| 生物学：**自然选择** | ↔ | 计算机：**遗传算法** |
| 物理学：**退火过程** | ↔ | 优化领域：**模拟退火** |
| 神经科学：**神经网络** | ↔ | 深度学习：**人工神经网络** |
| 经济学：**博弈论** | ↔ | 多智能体：**强化学习** |

**Knowledge Nexus** 旨在：
1. **构建领域内知识图谱** — 梳理单个领域中各 SOTA 工作之间的引用、继承、改进关系
2. **发现跨领域关联** — 利用 AI 识别不同领域知识之间的结构相似性与概念迁移
3. **生成新知识假说** — 基于已有关联模式，推断潜在的跨域启发与创新方向

## 📐 系统架构

```mermaid
graph TB
    subgraph Frontend["🖥️ 前端 — React + TypeScript"]
        direction LR
        GV["📊 图谱可视化<br/><i>Cytoscape.js</i>"]
        KM["📚 知识库管理"]
        AI["🤖 AI 发现引擎<br/><i>三标签面板</i>"]
        CR["🕷️ 爬虫控制台"]
    end

    subgraph Backend["⚙️ 后端 — FastAPI + Python"]
        direction LR
        PS["📄 论文服务"]
        GS["🕸️ 图谱服务"]
        AE["🧠 AI 引擎<br/><i>LLM 分析器</i>"]
        CS["🔍 爬虫服务"]
    end

    subgraph Storage["💾 数据层"]
        direction LR
        DB[("🗄️ SQLite / PostgreSQL<br/><i>论文 · 知识节点 · 关系</i>")]
        FS["📁 文件存储<br/><i>PDF 论文</i>"]
    end

    subgraph External["🌐 外部服务"]
        direction LR
        LLM["🤖 LLM API<br/><i>豆包 · DeepSeek<br/>OpenAI · Ollama</i>"]
        OA["📖 OpenAlex<br/><i>论文元数据</i>"]
        SS["🔬 Semantic Scholar<br/><i>引用数据</i>"]
    end

    Frontend -->|"REST API<br/>(Vite 代理)"| Backend
    PS --> DB
    PS --> FS
    GS --> DB
    AE --> LLM
    AE --> DB
    CS --> OA
    CS --> SS
    CS --> DB

    style Frontend fill:#e6f3ff,stroke:#4a90d9,stroke-width:2px
    style Backend fill:#f0f7e6,stroke:#5cb85c,stroke-width:2px
    style Storage fill:#fff8e6,stroke:#f0ad4e,stroke-width:2px
    style External fill:#fce6f0,stroke:#d9534f,stroke-width:2px
```

### 数据流

```mermaid
flowchart LR
    A["📥 导入<br/><i>脚本 · 爬虫 · 手动</i>"] --> B["🗄️ 知识库<br/><i>节点 + 论文 + 关系</i>"]
    B --> C["🕸️ 图谱可视化<br/><i>Cytoscape.js</i>"]
    B --> D["🧠 AI 发现引擎<br/><i>LLM 分析</i>"]
    D -->|"新关联<br/>& 假说"| B
    D --> E["💡 新知识<br/><i>跨领域洞见</i>"]

    style A fill:#e8f5e9,stroke:#4caf50
    style B fill:#e3f2fd,stroke:#2196f3
    style C fill:#fff3e0,stroke:#ff9800
    style D fill:#fce4ec,stroke:#e91e63
    style E fill:#f3e5f5,stroke:#9c27b0
```

## ✨ 核心功能

### 📚 知识库管理
- 多类型知识节点：论文、概念、现象、定理、方法、原理
- 论文元数据管理，支持 PDF 存储、DOI、引用量
- 多领域支持：计算机科学、语音AI、生物学、物理学、数学等 13+ 领域
- 支持脚本批量导入和爬虫自动采集

### 🕸️ 交互式知识图谱
- 基于 **Cytoscape.js** 的图谱可视化，节点按领域着色
- 关键词搜索、领域过滤、跨域模式切换
- 缩放、拖拽、点击聚焦等交互操作
- 多种关系类型：引用(CITES)、继承(BUILDS_ON)、改进(IMPROVES)、类比(ANALOGOUS_TO)、启发(INSPIRES)、组成(PART_OF)、使能(ENABLES)

### 🤖 AI 发现引擎（LLM 驱动）
- **🔍 跨域发现** — AI 分析知识节点，发现不同领域间的隐藏关联
- **🔬 配对分析** — 深入分析任意两个节点之间的关系
- **🧠 知识推导** — 选择多个节点，让 AI 推导出新的见解和假说
- 支持领域过滤，聚焦特定领域的发现
- 三级模糊匹配策略，确保节点识别的鲁棒性
- 兼容任何 OpenAI 格式的 LLM API（豆包、DeepSeek、OpenAI、Ollama）

### 🕷️ 智能论文爬取
- 多数据源爬取：OpenAlex、Semantic Scholar、arXiv
- 基于引用量、顶会/顶刊、SOTA 记录的质量评分
- 自动下载 Open Access 论文 PDF
- 限流、断点续爬、去重

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | React 18, TypeScript, Ant Design, Cytoscape.js, Vite |
| **后端** | Python 3.11+, FastAPI, SQLAlchemy, Pydantic |
| **数据库** | SQLite (开发), PostgreSQL (生产) |
| **AI/LLM** | OpenAI 兼容 API（豆包, DeepSeek, OpenAI, Ollama） |
| **爬虫** | httpx, OpenAlex API, Semantic Scholar API |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- LLM API Key（豆包 / DeepSeek / OpenAI 或本地 Ollama）

### 1. 克隆仓库

```bash
git clone https://github.com/Harris-H/knowledge-nexus.git
cd knowledge-nexus
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（自动代理 API 到后端）
npm run dev
```

### 4. 初始化知识库（可选）

```bash
cd scripts
python add_cross_domain_knowledge.py
python add_cross_domain_knowledge_v2.py
python add_cs_knowledge_v3.py
python add_speech_ai_knowledge.py
python update_speech_domain.py
```

### 5. 打开浏览器

访问终端显示的地址（默认 `http://localhost:3001`）。

## 📁 项目结构

```
knowledge-nexus/
├── README.md                    # 英文文档
├── README_zh.md                 # 中文文档（本文件）
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── api/                 # API 路由（论文、图谱、AI、爬虫）
│   │   ├── models/              # SQLAlchemy 模型（Paper, KnowledgeNode, Relation）
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── services/            # 业务逻辑
│   │   │   ├── ai/              # LLM 驱动的发现引擎
│   │   │   ├── crawler/         # 论文爬取服务
│   │   │   └── ...
│   │   └── core/                # 配置、数据库初始化
│   ├── .env.example             # 环境变量模板
│   └── requirements.txt
├── frontend/                    # React + TypeScript 前端
│   ├── src/
│   │   ├── pages/               # 主要页面
│   │   │   ├── GraphPage.tsx    # 知识图谱可视化
│   │   │   ├── AIDiscoveryPage.tsx  # AI 发现（3 标签页）
│   │   │   ├── PapersPage.tsx   # 论文管理
│   │   │   ├── KnowledgeNodesPage.tsx  # 知识节点管理
│   │   │   └── CrawlerPage.tsx  # 论文爬虫
│   │   ├── api/                 # API 客户端
│   │   ├── components/          # 通用组件
│   │   └── types/               # TypeScript 类型定义
│   └── package.json
├── scripts/                     # 数据导入脚本
├── docs/                        # 设计文档
│   ├── tech-stack.md            # 技术栈详解
│   ├── architecture.md          # 架构设计
│   ├── api-design.md            # API 设计
│   └── crawler-design.md        # 爬虫模块设计
├── storage/                     # 文件存储（PDF）
└── docker-compose.yml           # Docker 编排（可选）
```

## 📊 当前知识库

| 领域 | 知识节点 | 论文 | 说明 |
|------|---------|------|------|
| 💻 计算机科学 | 49 | ~26 | 完整 AI 技术栈：反向传播 → Transformer → LLM → Agent → MCP |
| 🎤 语音 AI | 12 | 18 | ASR、TTS、语音克隆、神经音频编解码、语音大模型 |
| 🧬 生物学 | 6 | - | 进化、遗传、神经系统 |
| ⚛️ 物理学 | 4 | - | 热力学、量子力学 |
| 📊 数学 | 4 | - | 图论、优化、概率论 |
| 🧠 神经科学 | 3 | - | 神经可塑性、记忆 |
| 🧪 化学 | 2 | - | 催化作用、分子自组装 |
| + 其他 6 个领域 | ... | ... | 心理学、生态学、哲学、社会学、经济学、工程学 |

**总计：135+ 节点，247+ 关系，13 个领域**

## 🤖 LLM 配置

Knowledge Nexus 支持任何 OpenAI 兼容的 LLM API。编辑 `backend/.env`：

```bash
# 豆包（字节跳动）— 默认
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_MODEL=doubao-seed-2-0-lite-260215

# DeepSeek
# LLM_BASE_URL=https://api.deepseek.com/v1
# LLM_MODEL=deepseek-chat

# OpenAI
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-4o-mini

# 本地 Ollama
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL=qwen2.5
```

## 📸 截图

> 即将添加 — 图谱可视化、AI 发现面板、知识管理界面

## 🗺️ 开发路线

- [ ] 基于向量嵌入的语义搜索
- [ ] PDF 自动解析与元数据提取
- [ ] 多用户协作
- [ ] 知识时间线视图
- [ ] 导出为标准格式（RDF、OWL）
- [ ] 自定义领域适配器插件系统

## 📄 开源协议

MIT
