# Knowledge Nexus — Cross-Domain Knowledge Association Engine

[English](#-vision) | [中文](#-项目愿景)

> Discover deep connections between seemingly unrelated concepts across domains. Weave isolated knowledge into an interconnected intelligence network, powered by AI.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Vision

Human knowledge is scattered across disciplines, yet many concepts are deeply connected:

| Domain A | ↔ | Domain B |
|---|---|---|
| Biology: **Natural Selection** | ↔ | CS: **Genetic Algorithm** |
| Physics: **Annealing** | ↔ | Optimization: **Simulated Annealing** |
| Neuroscience: **Neural Networks** | ↔ | Deep Learning: **Artificial Neural Networks** |
| Economics: **Game Theory** | ↔ | Multi-Agent: **Reinforcement Learning** |

**Knowledge Nexus** aims to:
1. **Build intra-domain knowledge graphs** — Map citation, inheritance, and improvement relationships between SOTA works within a domain
2. **Discover cross-domain associations** — Use AI to identify structural similarities and concept transfers across fields
3. **Generate new knowledge hypotheses** — Infer potential cross-domain inspirations and innovation directions

## ✨ Features

### 📚 Knowledge Base Management
- Multi-type knowledge nodes: papers, concepts, phenomena, theorems, methods, principles
- Paper metadata with PDF storage, DOI, citation counts
- Multi-domain support: Computer Science, Speech AI, Biology, Physics, Mathematics, and more
- Batch import via scripts or crawler

### 🕸️ Interactive Knowledge Graph
- **Cytoscape.js**-powered graph visualization with domain-colored nodes
- Search by keyword, filter by domain, toggle cross-domain mode
- Zoom, pan, drag, and click-to-focus interactions
- Multiple relation types: CITES, BUILDS_ON, IMPROVES, ANALOGOUS_TO, INSPIRES, PART_OF, ENABLES

### 🤖 AI Discovery Engine (LLM-Powered)
- **Cross-Domain Discovery** — AI analyzes knowledge nodes to find hidden associations across domains
- **Pair Analysis** — Deep dive into the relationship between any two selected nodes
- **Knowledge Derivation** — Select multiple nodes and let AI derive new insights and hypotheses
- Domain filtering to focus discovery on specific fields
- Fuzzy matching with 3-level strategy for robust node identification
- Compatible with any OpenAI-format LLM API (Doubao, DeepSeek, OpenAI, Ollama)

### 🕷️ Smart Paper Crawler
- Multi-source crawling: OpenAlex, Semantic Scholar, arXiv
- Quality scoring based on citation count, venue prestige, and SOTA records
- Auto-download Open Access PDFs
- Rate-limited, resumable, deduplicated

### 🔍 Graph Exploration
- Domain-filtered subgraphs
- Cross-domain mode highlighting inter-field connections
- Node detail panel with full metadata

## 📐 Architecture

```
┌───────────────────────────────────────────────────────┐
│                  Frontend (React + TS)                  │
│  ┌────────────┐ ┌─────────────┐ ┌──────────────────┐  │
│  │ Graph View  │ │ Knowledge   │ │  AI Discovery    │  │
│  │ (Cytoscape) │ │ Management  │ │  (3-Tab Panel)   │  │
│  └────────────┘ └─────────────┘ └──────────────────┘  │
└───────────────────────┬───────────────────────────────┘
                        │ REST API (Proxy via Vite)
┌───────────────────────┴───────────────────────────────┐
│                  Backend (FastAPI)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Papers   │ │ Graph    │ │ AI Engine│ │ Crawler  │ │
│  │ Service  │ │ Service  │ │ (LLM)   │ │ Service  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
└───────┼────────────┼────────────┼────────────┼────────┘
        │            │            │            │
   ┌────┴────┐  ┌────┴────┐ ┌────┴────┐ ┌────┴────────┐
   │ SQLite  │  │ SQLite  │ │ LLM API │ │ OpenAlex /  │
   │ (Data)  │  │(Relations│ │(Doubao/ │ │ Semantic    │
   │         │  │ & Graph)│ │DeepSeek)│ │ Scholar     │
   └─────────┘  └─────────┘ └─────────┘ └─────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Ant Design, Cytoscape.js, Vite |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Pydantic |
| **Database** | SQLite (dev), PostgreSQL (prod-ready) |
| **AI/LLM** | OpenAI-compatible API (Doubao, DeepSeek, OpenAI, Ollama) |
| **Crawler** | httpx, OpenAlex API, Semantic Scholar API |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An LLM API key (Doubao, DeepSeek, OpenAI, or local Ollama)

### 1. Clone the Repository

```bash
git clone https://github.com/Harris-H/knowledge-nexus.git
cd knowledge-nexus
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set your LLM_API_KEY

# Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (auto-proxies API to backend)
npm run dev
```

### 4. Initialize Knowledge Base (Optional)

```bash
# Add cross-domain knowledge nodes
cd scripts
python add_cross_domain_knowledge.py
python add_cross_domain_knowledge_v2.py
python add_cs_knowledge_v3.py
python add_speech_ai_knowledge.py
python update_speech_domain.py
```

### 5. Open in Browser

Visit `http://localhost:3001` (or the port shown in terminal).

## 📁 Project Structure

```
knowledge-nexus/
├── README.md                    # This file
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── api/                 # API routes (papers, graph, ai, crawler)
│   │   ├── models/              # SQLAlchemy models (Paper, KnowledgeNode, Relation)
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Business logic
│   │   │   ├── ai/              # LLM-powered discovery engine
│   │   │   ├── crawler/         # Paper crawling service
│   │   │   └── ...
│   │   └── core/                # Config, database setup
│   ├── .env.example             # Environment template
│   └── requirements.txt
├── frontend/                    # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/               # Main pages
│   │   │   ├── GraphPage.tsx    # Knowledge graph visualization
│   │   │   ├── AIDiscoveryPage.tsx  # AI discovery (3 tabs)
│   │   │   ├── PapersPage.tsx   # Paper management
│   │   │   ├── KnowledgeNodesPage.tsx  # Knowledge node management
│   │   │   └── CrawlerPage.tsx  # Paper crawler
│   │   ├── api/                 # API client
│   │   ├── components/          # Shared components
│   │   └── types/               # TypeScript types
│   └── package.json
├── scripts/                     # Data import scripts
├── docs/                        # Design documents
│   ├── tech-stack.md
│   ├── architecture.md
│   ├── api-design.md
│   └── crawler-design.md
├── storage/                     # File storage (PDFs)
└── docker-compose.yml           # Docker setup (optional)
```

## 📊 Current Knowledge Base

| Domain | Nodes | Papers | Description |
|--------|-------|--------|-------------|
| 💻 Computer Science | 49 | ~26 | Full AI stack: Backpropagation → Transformer → LLM → Agent → MCP |
| 🎤 Speech AI | 12 | 18 | ASR, TTS, Voice Cloning, Neural Audio Codec, Speech LLM |
| 🧬 Biology | 6 | - | Evolution, genetics, neural systems |
| ⚛️ Physics | 4 | - | Thermodynamics, quantum mechanics |
| 📊 Mathematics | 4 | - | Graph theory, optimization, probability |
| 🧠 Neuroscience | 3 | - | Neural plasticity, memory |
| 🧪 Chemistry | 2 | - | Catalysis, molecular self-assembly |
| + 6 more domains | ... | ... | Psychology, ecology, philosophy, sociology, economics, engineering |

**Total: 135+ nodes, 247+ relations, 13 domains**

## 🤖 LLM Configuration

Knowledge Nexus supports any OpenAI-compatible LLM API. Edit `backend/.env`:

```bash
# Doubao (ByteDance) — Default
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_MODEL=doubao-seed-2-0-lite-260215

# DeepSeek
# LLM_BASE_URL=https://api.deepseek.com/v1
# LLM_MODEL=deepseek-chat

# OpenAI
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-4o-mini

# Local Ollama
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL=qwen2.5
```

## 📸 Screenshots

> Coming soon — Graph visualization, AI Discovery panel, Knowledge management

## 🗺️ Roadmap

- [ ] Semantic search with vector embeddings
- [ ] PDF auto-parsing and metadata extraction
- [ ] Multi-user collaboration
- [ ] Knowledge timeline view
- [ ] Export to standard formats (RDF, OWL)
- [ ] Plugin system for custom domain adapters

## 📄 License

MIT

---

---

# 中文文档

## 🎯 项目愿景

人类知识分散在不同领域中，但本质上许多概念跨域相通：

- 生物学的 **自然选择** ↔ 计算机的 **遗传算法**
- 物理学的 **退火过程** ↔ 优化领域的 **模拟退火**
- 神经科学的 **神经网络** ↔ 深度学习的 **人工神经网络**
- 经济学的 **博弈论** ↔ 多智能体的 **强化学习**

**Knowledge Nexus** 旨在：
1. **构建领域内知识图谱** — 梳理单个领域中各 SOTA 工作之间的引用、继承、改进关系
2. **发现跨领域关联** — 利用 AI 识别不同领域知识之间的结构相似性与概念迁移
3. **生成新知识假说** — 基于已有关联模式，推断潜在的跨域启发与创新方向

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
- 多种关系类型：引用、继承、改进、类比、启发、组成、使能

### 🤖 AI 发现引擎（LLM 驱动）
- **跨域发现** — AI 分析知识节点，发现不同领域间的隐藏关联
- **配对分析** — 深入分析任意两个节点之间的关系
- **知识推导** — 选择多个节点，让 AI 推导出新的见解和假说
- 支持领域过滤，聚焦特定领域的发现
- 三级模糊匹配策略，确保节点识别的鲁棒性
- 兼容任何 OpenAI 格式的 LLM API（豆包、DeepSeek、OpenAI、Ollama）

### 🕷️ 智能论文爬取
- 多数据源爬取：OpenAlex、Semantic Scholar、arXiv
- 基于引用量、顶会/顶刊、SOTA 记录的质量评分
- 自动下载 Open Access 论文 PDF
- 限流、断点续爬、去重

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- LLM API Key（豆包/DeepSeek/OpenAI 或本地 Ollama）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Harris-H/knowledge-nexus.git
cd knowledge-nexus

# 2. 后端设置
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY
uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload

# 3. 前端设置（新终端）
cd frontend
npm install
npm run dev

# 4.（可选）初始化知识库
cd scripts
python add_cross_domain_knowledge.py
python add_cs_knowledge_v3.py
python add_speech_ai_knowledge.py
```

### 打开浏览器

访问终端显示的地址（默认 `http://localhost:3001`）。

## 📄 开源协议

MIT
