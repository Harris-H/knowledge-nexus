# API 设计文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **文件上传**: multipart/form-data

## API 概览

| 模块 | 前缀 | 说明 |
|------|------|------|
| 论文管理 | `/papers` | 论文 CRUD、导入、PDF 管理 |
| 知识图谱 | `/graph` | 图谱查询、关联管理 |
| AI 引擎 | `/ai` | 关联发现、假说生成 |
| 检索 | `/search` | 多模态搜索 |
| 领域 | `/domains` | 领域分类管理 |
| 概念 | `/concepts` | 概念管理 |
| 用户 | `/auth` | 认证与用户管理 |

---

## 1. 论文管理 `/papers`

### 上传论文
```http
POST /papers
Content-Type: multipart/form-data

Fields:
  - file: PDF 文件（可选）
  - title: string (required)
  - abstract: string
  - authors: string[] 
  - year: integer
  - domain_id: string
  - tags: string[]
  - url: string (论文链接)

Response 201:
{
  "id": "paper_abc123",
  "title": "Attention Is All You Need",
  "status": "processing",  // PDF 正在解析中
  "created_at": "2026-03-15T10:00:00Z"
}
```

### 获取论文详情
```http
GET /papers/{paper_id}

Response 200:
{
  "id": "paper_abc123",
  "title": "Attention Is All You Need",
  "abstract": "The dominant sequence transduction models...",
  "authors": ["Vaswani, A.", "Shazeer, N.", ...],
  "year": 2017,
  "domain": { "id": "cs-nlp", "name": "自然语言处理" },
  "tags": ["transformer", "attention", "seq2seq"],
  "pdf_url": "/storage/papers/paper_abc123.pdf",
  "key_contributions": [
    "提出 Self-Attention 机制替代 RNN",
    "多头注意力并行计算",
    "位置编码方案"
  ],
  "relations": {
    "cites": 12,
    "cited_by": 8,
    "improves": 2,
    "cross_domain": 1
  },
  "ai_status": "analyzed",  // pending | analyzing | analyzed
  "created_at": "2026-03-15T10:00:00Z"
}
```

### 论文列表
```http
GET /papers?domain={domain_id}&year={year}&tag={tag}&page=1&size=20&sort=year

Response 200:
{
  "items": [...],
  "total": 156,
  "page": 1,
  "size": 20
}
```

### 批量导入
```http
POST /papers/import/arxiv
Body: { "arxiv_ids": ["2401.12345", "2312.67890"] }

POST /papers/import/doi
Body: { "dois": ["10.1234/xxxxx"] }

POST /papers/import/bibtex
Content-Type: multipart/form-data
Fields: file (*.bib)
```

---

## 2. 知识图谱 `/graph`

### 获取子图
```http
GET /graph/subgraph?center={node_id}&depth=2&limit=50&type=paper,concept

Response 200:
{
  "nodes": [
    {
      "id": "paper_abc123",
      "type": "paper",
      "label": "Attention Is All You Need",
      "properties": { "year": 2017, "domain": "NLP" },
      "position": { "x": 0, "y": 0 }  // 可选，前端可自行布局
    },
    {
      "id": "concept_transformer",
      "type": "concept",
      "label": "Transformer",
      "properties": { "domain": "Deep Learning" }
    }
  ],
  "edges": [
    {
      "id": "rel_001",
      "source": "paper_abc123",
      "target": "paper_def456",
      "type": "IMPROVES",
      "properties": {
        "description": "引入多头注意力机制改进序列建模",
        "confidence": 0.95,
        "ai_generated": false
      }
    }
  ],
  "stats": {
    "total_nodes": 42,
    "total_edges": 67
  }
}
```

### 查询关联路径
```http
GET /graph/path?from={node_id}&to={node_id}&max_depth=5

Response 200:
{
  "paths": [
    {
      "length": 3,
      "nodes": ["paper_a", "concept_x", "concept_y", "paper_b"],
      "edges": [
        { "type": "INTRODUCES", ... },
        { "type": "ANALOGOUS_TO", ... },
        { "type": "USES", ... }
      ]
    }
  ]
}
```

### 添加关联
```http
POST /graph/relations
Body:
{
  "source_id": "paper_abc123",
  "target_id": "paper_def456",
  "relation_type": "IMPROVES",
  "description": "在 Transformer 基础上引入稀疏注意力",
  "properties": {}
}
```

---

## 3. AI 引擎 `/ai`

### 分析论文关联
```http
POST /ai/analyze-paper
Body: { "paper_id": "paper_abc123" }

Response 202:
{
  "task_id": "task_xyz",
  "status": "queued",
  "message": "论文关联分析任务已加入队列"
}
```

### 触发跨领域发现
```http
POST /ai/discover-cross-domain
Body:
{
  "source_domain": "computer-science",
  "target_domain": "biology",    // 可选，不指定则全域扫描
  "concept_id": "concept_xxx",   // 可选，指定起点概念
  "limit": 10
}

Response 202:
{
  "task_id": "task_xyz",
  "status": "queued"
}
```

### 获取 AI 建议列表
```http
GET /ai/suggestions?status=pending&type=cross_domain&page=1

Response 200:
{
  "items": [
    {
      "id": "sug_001",
      "type": "cross_domain_analogy",
      "source": { "id": "concept_natural_selection", "name": "自然选择", "domain": "生物学" },
      "target": { "id": "concept_genetic_algo", "name": "遗传算法", "domain": "计算机科学" },
      "confidence": 0.92,
      "explanation": "两者都基于'适者生存'的筛选机制...",
      "potential_innovations": [
        "将表观遗传学的环境适应机制引入遗传算法的变异策略"
      ],
      "status": "pending",  // pending | approved | rejected | modified
      "created_at": "2026-03-15T10:00:00Z"
    }
  ]
}
```

### 审核 AI 建议
```http
POST /ai/suggestions/{id}/review
Body:
{
  "action": "approve",  // approve | reject | modify
  "comment": "关联合理，已确认",
  "modifications": {}   // action=modify 时提供修改内容
}
```

---

## 4. 检索 `/search`

### 统一搜索
```http
GET /search?q=transformer+attention&mode=hybrid&domain=cs&limit=20

Response 200:
{
  "results": [
    {
      "id": "paper_abc123",
      "type": "paper",
      "title": "Attention Is All You Need",
      "snippet": "...我们提出了一种新的 <em>Transformer</em> 架构...",
      "score": 0.95,
      "match_source": "keyword+semantic"  // 匹配来源
    }
  ],
  "facets": {
    "domains": [{ "id": "cs", "name": "计算机", "count": 15 }],
    "years": [{ "year": 2017, "count": 3 }]
  }
}
```

### 查找跨域相似概念
```http
GET /search/cross-domain/{concept_id}?limit=10

Response 200:
{
  "source_concept": { "id": "xxx", "name": "自然选择", "domain": "生物学" },
  "similar_concepts": [
    {
      "id": "yyy",
      "name": "遗传算法",
      "domain": "计算机科学",
      "similarity": 0.87,
      "explanation": "共享进化筛选的核心机制"
    }
  ]
}
```

---

## 5. 通用约定

### 错误响应格式
```json
{
  "error": {
    "code": "PAPER_NOT_FOUND",
    "message": "论文不存在",
    "details": {}
  }
}
```

### HTTP 状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 202 | 异步任务已接受 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

### 分页
所有列表接口统一使用 `page` + `size` 分页参数，响应包含 `total` 总数。
