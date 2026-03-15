# 架构设计文档

## 1. 设计原则

- **领域驱动**：以「论文」「概念」「领域」「关联」为核心领域模型
- **AI 原生**：AI 不是附加功能，而是系统的核心引擎
- **渐进增强**：先做好领域内图谱，再扩展到跨领域关联
- **人机协同**：AI 提出假说，人类确认/修正，形成正反馈循环

## 2. 系统分层架构

```
┌─────────────────────────────────────────────────┐
│               Presentation Layer                 │
│  React SPA + Cytoscape.js Graph Visualization   │
├─────────────────────────────────────────────────┤
│               API Gateway Layer                  │
│  FastAPI Router + Auth Middleware + Rate Limit   │
├─────────────────────────────────────────────────┤
│               Service Layer                      │
│  PaperService | GraphService | AIService |      │
│  SearchService | UserService                     │
├─────────────────────────────────────────────────┤
│               Domain Layer                       │
│  Paper | Concept | Domain | Relation | Author   │
├─────────────────────────────────────────────────┤
│               Infrastructure Layer               │
│  Neo4j | PostgreSQL | Qdrant | Meilisearch |    │
│  Redis | File Storage                            │
└─────────────────────────────────────────────────┘
```

## 3. 核心模块设计

### 3.1 论文管理模块 (Paper Service)

**职责**：论文的增删改查、PDF 上传与解析、元数据管理

```
用户上传 PDF
    │
    ▼
PDF 存储到 storage/papers/
    │
    ▼
异步任务：PDF 解析（PyMuPDF / GROBID）
    │
    ├─→ 提取: 标题、作者、摘要、年份、参考文献列表
    ├─→ 生成: 论文摘要的 Embedding 向量
    ├─→ 存储: 元数据 → PostgreSQL
    ├─→ 存储: 向量 → Qdrant
    ├─→ 索引: 标题+摘要 → Meilisearch
    └─→ 创建: 论文节点 → Neo4j
```

**关键接口**：
- `POST /api/papers` — 上传论文（PDF + 基本信息）
- `GET /api/papers/{id}` — 获取论文详情
- `GET /api/papers` — 论文列表（分页、筛选）
- `POST /api/papers/import/arxiv` — 从 arXiv ID 导入
- `POST /api/papers/import/doi` — 从 DOI 导入
- `POST /api/papers/import/bibtex` — 批量 BibTeX 导入

### 3.2 知识图谱模块 (Graph Service)

**职责**：图谱的构建、查询、可视化数据提供

**节点类型**：
| 类型 | 属性 | 说明 |
|------|------|------|
| Paper | id, title, abstract, year, domain, impact_score | 论文节点 |
| Concept | id, name, description, domain | 概念节点 |
| Domain | id, name, description, parent_domain | 领域节点（支持层级） |
| Author | id, name, affiliation | 作者节点 |

**关系类型**：
| 关系 | 方向 | 属性 | 说明 |
|------|------|------|------|
| CITES | Paper → Paper | year | 引用 |
| IMPROVES | Paper → Paper | aspect, description | 改进 |
| INSPIRED_BY | Paper → Paper | description | 受启发 |
| CONTRADICTS | Paper → Paper | description | 矛盾/挑战 |
| INTRODUCES | Paper → Concept | — | 论文提出某概念 |
| USES | Paper → Concept | — | 论文使用某概念 |
| ANALOGOUS_TO | Concept → Concept | similarity_score, explanation | **跨域类比（核心）** |
| DERIVED_FROM | Concept → Concept | — | 概念衍生 |
| BELONGS_TO | Paper/Concept → Domain | — | 所属领域 |

**关键接口**：
- `GET /api/graph/subgraph` — 获取子图（按领域/论文/概念中心展开）
- `GET /api/graph/path` — 查询两节点间的关联路径
- `GET /api/graph/neighbors/{node_id}` — 获取邻居节点
- `POST /api/graph/relations` — 手动添加关联
- `GET /api/graph/stats` — 图谱统计信息

### 3.3 AI 引擎模块 (AI Service)

**职责**：自动发现关联、生成知识假说、辅助分析

#### 3.3.1 领域内关联发现

```
新论文入库
    │
    ▼
Embedding 向量相似度检索（Qdrant）
    │ 返回 Top-K 相似论文
    ▼
LLM 深度分析（Prompt Engineering）
    │ 输入：新论文摘要 + 相似论文摘要
    │ 输出：关联类型 + 置信度 + 解释
    ▼
写入候选关联队列
    │
    ▼
用户审核确认 / 自动采纳（高置信度）
```

#### 3.3.2 跨领域关联发现（核心创新）

```
定期批量任务 / 用户触发
    │
    ▼
概念级 Embedding 检索
    │ 在 Qdrant 中跨领域搜索语义相似概念
    │ 例：搜索 "遗传" 概念的跨域近邻
    ▼
候选跨域概念对
    │ (生物:自然选择, 计算机:遗传算法)
    │ (物理:退火, 优化:模拟退火)
    ▼
LLM 跨域分析
    │ Prompt: "分析以下两个不同领域的概念，
    │          判断它们之间是否存在知识迁移关系，
    │          如果存在，解释迁移的本质和可能的新应用方向"
    ▼
生成跨域关联假说
    │ 包含：关联描述、迁移本质、创新启发、置信度
    ▼
人机协同审核
```

#### 3.3.3 新知识生成

```
已确认的跨域关联集合
    │
    ▼
LLM 创意推理
    │ Prompt: "基于已发现的跨域关联模式，
    │          推断以下领域 X 的概念 Y 
    │          可能在领域 Z 中产生什么样的新方法/应用"
    ▼
新知识假说
    │ 包含：假说描述、推理链、可行性评估、验证建议
    ▼
存入知识库，标记为 "AI生成-待验证"
```

**关键接口**：
- `POST /api/ai/analyze-paper` — 分析单篇论文的关联
- `POST /api/ai/discover-cross-domain` — 触发跨领域关联发现
- `POST /api/ai/generate-hypothesis` — 生成新知识假说
- `GET /api/ai/pending-reviews` — 待审核的 AI 建议列表
- `POST /api/ai/review/{id}` — 审核 AI 建议（确认/否决/修改）

### 3.4 检索模块 (Search Service)

**职责**：多模态搜索（关键词 + 语义 + 图结构）

**搜索模式**：
1. **关键词搜索**：Meilisearch 全文检索，支持模糊匹配、中文分词
2. **语义搜索**：Qdrant 向量近邻，找到语义相近但措辞不同的内容
3. **图搜索**：Neo4j Cypher 查询，沿关联路径探索
4. **混合搜索**：综合以上三种结果，加权排序

**关键接口**：
- `GET /api/search?q=xxx&mode=keyword|semantic|graph|hybrid`
- `GET /api/search/similar/{paper_id}` — 查找相似论文
- `GET /api/search/cross-domain/{concept_id}` — 查找跨领域类似概念

## 4. 数据流全景

```
                    ┌──────────┐
                    │  用户操作  │
                    └─────┬────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
         上传论文     浏览图谱      搜索
              │           │           │
              ▼           ▼           ▼
         ┌────────┐  ┌────────┐  ┌────────┐
         │Paper   │  │Graph   │  │Search  │
         │Service │  │Service │  │Service │
         └───┬────┘  └────┬───┘  └────┬───┘
             │            │           │
    ┌────────┼────────────┼───────────┼────────┐
    │        ▼            ▼           ▼        │
    │   PostgreSQL     Neo4j     Meilisearch   │
    │        │            ▲        Qdrant      │
    │        │            │           │        │
    │        ▼            │           │        │
    │   ┌─────────┐       │           │        │
    │   │AI Service├──────┘───────────┘        │
    │   │(异步任务) │  写入关联/读取向量         │
    │   └─────────┘                            │
    │            Infrastructure                 │
    └──────────────────────────────────────────┘
```

## 5. 扩展性考虑

### Phase 1 — MVP（最小可用产品）
- 单领域（计算机科学）论文管理
- 手动添加关联 + 基础 AI 建议
- 基础图谱可视化
- 关键词搜索

### Phase 2 — 智能化
- 多领域支持
- 自动 PDF 解析
- AI 自动发现领域内关联
- 语义搜索

### Phase 3 — 跨域创新
- 跨领域关联发现
- 新知识假说生成
- 关联模式学习
- 协作功能（多用户共建图谱）

### Phase 4 — 生态化
- 插件系统（接入不同学术数据源）
- API 开放平台
- 社区共建知识图谱
- 移动端支持
