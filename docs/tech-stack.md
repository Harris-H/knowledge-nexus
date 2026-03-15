# 技术栈详解

## 总览

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **前端** | React 18 + TypeScript | 现代化 SPA 框架 |
| **图谱可视化** | Cytoscape.js | 专业级图可视化库，支持大规模图渲染 |
| **UI 组件库** | Ant Design 5 | 成熟的企业级 UI 组件 |
| **状态管理** | Zustand | 轻量、直观的状态管理 |
| **后端框架** | FastAPI (Python) | 高性能异步框架，天然适配 AI/ML 生态 |
| **图数据库** | Neo4j | 业界领先的原生图数据库 |
| **关系数据库** | PostgreSQL | 存储结构化论文元数据 |
| **全文检索** | Meilisearch | 轻量高速的搜索引擎，支持中文 |
| **向量数据库** | Qdrant | 存储论文/概念的语义向量，支持相似度检索 |
| **AI/LLM** | OpenAI API + 本地模型 | 关联发现与知识生成 |
| **PDF 解析** | PyMuPDF + GROBID | 论文 PDF 结构化提取 |
| **容器化** | Docker + Docker Compose | 一键部署所有服务 |

---

## 前端技术栈

### React 18 + TypeScript
- **选择理由**：生态成熟，TypeScript 提供类型安全，适合复杂数据驱动应用
- **构建工具**：Vite — 极速热更新，优秀的开发体验

### Cytoscape.js（图谱可视化）
- **选择理由**：
  - 专为图/网络可视化设计，API 丰富
  - 内置多种布局算法（force-directed, hierarchical, concentric 等）
  - 支持数万节点的流畅渲染
  - 丰富的交互支持（缩放、拖拽、框选、tooltip）
  - 插件生态好（cytoscape-cola, cytoscape-dagre 等）
- **备选方案**：D3.js（更底层灵活，但开发成本高）、vis.js、G6

### Ant Design 5
- **选择理由**：组件丰富、文档完善、对中文友好、主题定制灵活

### Zustand
- **选择理由**：比 Redux 轻量，API 直观，支持中间件，无 Provider 嵌套

---

## 后端技术栈

### FastAPI (Python 3.11+)
- **选择理由**：
  - 原生 async/await 支持，高并发性能优秀
  - 自动生成 OpenAPI 文档
  - Python 生态可直接调用 AI/ML 库（transformers, langchain 等）
  - Pydantic v2 数据验证，类型安全
- **ASGI 服务器**：Uvicorn

### 核心依赖
```
fastapi          — Web 框架
uvicorn          — ASGI 服务器
sqlalchemy       — ORM（PostgreSQL 交互）
neo4j            — Neo4j Python 驱动
pydantic         — 数据模型验证
python-multipart — 文件上传支持
celery + redis   — 异步任务队列（PDF解析、AI分析等耗时任务）
```

---

## 数据存储层

### Neo4j（图数据库）— 核心
- **用途**：存储知识图谱（节点 = 论文/概念/领域，边 = 关联关系）
- **选择理由**：
  - 原生图存储，关联查询性能远超关系型数据库
  - Cypher 查询语言直观强大
  - 支持图算法（最短路径、社区检测、PageRank 等）
  - 可视化工具 Neo4j Browser 便于调试
- **数据模型示例**：
  ```cypher
  // 节点类型
  (:Paper {id, title, abstract, year, domain, pdf_path, embedding})
  (:Concept {id, name, description, domain})
  (:Domain {id, name, description})
  (:Author {id, name, affiliation})

  // 关系类型
  (:Paper)-[:CITES]->(:Paper)              // 引用
  (:Paper)-[:IMPROVES]->(:Paper)           // 改进
  (:Paper)-[:INSPIRED_BY]->(:Paper)        // 启发
  (:Paper)-[:BELONGS_TO]->(:Domain)        // 所属领域
  (:Paper)-[:INTRODUCES]->(:Concept)       // 提出概念
  (:Paper)-[:AUTHORED_BY]->(:Author)       // 作者
  (:Concept)-[:ANALOGOUS_TO]->(:Concept)   // 跨域类比
  (:Concept)-[:DERIVED_FROM]->(:Concept)   // 衍生
  (:Concept)-[:BELONGS_TO]->(:Domain)      // 所属领域
  ```

### PostgreSQL（关系数据库）— 辅助
- **用途**：存储用户数据、系统配置、操作日志、论文结构化元数据备份
- **选择理由**：事务可靠、JSON 支持好、运维成熟

### Qdrant（向量数据库）
- **用途**：存储论文和概念的语义嵌入向量
- **选择理由**：
  - 高性能近似最近邻搜索（ANN）
  - 支持过滤条件 + 向量搜索的混合查询
  - 为跨领域语义相似度发现提供底层支持
- **工作流**：论文/概念 → Embedding 模型 → 向量 → Qdrant → 相似度检索

### Meilisearch（全文检索）
- **用途**：论文标题、摘要、关键词的全文搜索
- **选择理由**：零配置、毫秒级响应、原生支持中文分词、typo-tolerant

---

## AI / 智能层

### LLM 集成
- **主力模型**：OpenAI GPT-4o / Claude — 用于关联发现、知识生成
- **本地模型**（可选）：通过 Ollama 运行开源模型，降低成本保护隐私
- **调用方式**：LangChain 统一接口，支持切换不同模型

### Embedding 模型
- **用途**：将论文摘要/概念描述转化为语义向量
- **选型**：
  - `text-embedding-3-large`（OpenAI，高质量）
  - `bge-large-zh-v1.5`（本地，中文优化）
  - `sentence-transformers/all-MiniLM-L6-v2`（本地，轻量英文）

### AI 关联发现流程
```
1. 用户添加论文 → PDF 解析 → 提取摘要/关键贡献
2. 生成 Embedding → 存入 Qdrant
3. 向量相似度检索 → 找出语义近邻
4. LLM 深度分析 → 判断关联类型 + 生成解释
5. 写入 Neo4j 图谱 → 前端可视化展示
6. 跨领域扫描 → 定期批量发现潜在类比
```

### PDF 解析
- **PyMuPDF (fitz)**：提取文本、图片、表格
- **GROBID**（可选）：学术论文专用解析器，精确提取标题、作者、摘要、参考文献的结构化数据

---

## 基础设施

### Docker Compose 编排
```yaml
services:
  backend:    # FastAPI 应用
  frontend:   # React 应用 (Nginx)
  neo4j:      # 图数据库
  postgres:   # 关系数据库
  qdrant:     # 向量数据库
  meilisearch: # 搜索引擎
  redis:      # 缓存 + 任务队列
  grobid:     # PDF 解析服务（可选）
```

### 开发工具
- **代码规范**：ESLint + Prettier（前端），Ruff + Black（后端）
- **Git Hooks**：Husky + lint-staged
- **API 文档**：FastAPI 自动生成 Swagger UI
- **数据库迁移**：Alembic（PostgreSQL）

---

## 技术选型决策记录

| 决策点 | 选择 | 放弃方案 | 理由 |
|--------|------|----------|------|
| 图可视化 | Cytoscape.js | D3.js, vis.js, G6 | 图专用、API完善、性能好 |
| 后端语言 | Python | Go, Node.js | AI/ML 生态最好 |
| 图数据库 | Neo4j | ArangoDB, TigerGraph | 社区最大、文档最全、Cypher 易用 |
| 向量数据库 | Qdrant | Pinecone, Weaviate, Milvus | 开源、性能好、API 简洁 |
| 搜索引擎 | Meilisearch | Elasticsearch | 轻量、易部署、中文支持好 |
| 前端框架 | React | Vue 3 | 生态更大、TypeScript支持更好 |
