# 论文自动爬取模块设计

## 1. 概述

自动从多个学术数据源爬取计算机领域近 10 年的开创性工作，建立高质量种子知识库。

## 2. 数据源

### 2.1 Semantic Scholar API（主力）
- **优势**：免费、结构化好、有引用量/影响力指标、支持批量查询
- **API**：`https://api.semanticscholar.org/graph/v1/`
- **可获取字段**：标题、摘要、作者、年份、引用数、参考文献列表、研究领域、PDF 链接
- **限制**：100 请求/5 分钟（无 key），1 请求/秒（有 key 可提升）
- **适用场景**：按引用量筛选高影响力论文、获取引用关系图

### 2.2 arXiv API
- **优势**：开放、无需认证、支持全文 PDF 下载
- **API**：`http://export.arxiv.org/api/query`
- **可获取字段**：标题、摘要、作者、分类、PDF 链接、提交时间
- **限制**：建议间隔 3 秒/请求
- **适用场景**：获取 PDF 原文、补充 Semantic Scholar 缺失的论文

### 2.3 DBLP API
- **优势**：计算机科学专用、收录权威会议/期刊
- **API**：`https://dblp.org/search/publ/api`
- **可获取字段**：标题、作者、会议/期刊、年份、DOI
- **适用场景**：按顶会/顶刊筛选（CVPR, NeurIPS, ICML, ACL, SIGMOD 等）

### 2.4 Papers with Code
- **优势**：关联了论文 + 代码 + 数据集 + SOTA 排行榜
- **API**：`https://paperswithcode.com/api/v1/`
- **可获取字段**：论文信息、关联代码仓库、任务排名
- **适用场景**：获取 SOTA 工作及其基准测试表现

### 2.5 OpenAlex API
- **优势**：完全免费开放、数据量大、引用关系完整
- **API**：`https://api.openalex.org/`
- **可获取字段**：标题、摘要、作者、机构、引用数、概念标签、开放获取状态
- **适用场景**：大规模论文元数据获取、引用网络构建

## 3. 开创性工作筛选策略

### 3.1 定量指标
| 指标 | 阈值建议 | 说明 |
|------|----------|------|
| 引用量 | > 500（近5年）或 > 1000（5-10年） | 高被引论文 |
| 年引用增长 | 持续上升趋势 | 影响力仍在扩大的工作 |
| Influential Citations | > 100 (Semantic Scholar) | 非泛引，对后续工作有实质影响 |

### 3.2 定性指标
| 指标 | 来源 | 说明 |
|------|------|------|
| Best Paper Award | 会议官网 / DBLP | 顶会最佳论文 |
| 顶会/顶刊 | DBLP | NeurIPS, ICML, ICLR, CVPR, ACL, AAAI 等 |
| SOTA 记录 | Papers with Code | 刷新基准测试记录的工作 |
| 开创新范式 | AI/LLM 辅助判断 | 提出新概念/方法论的里程碑论文 |

### 3.3 子领域种子清单（计算机科学）

```yaml
computer_science:
  deep_learning:
    keywords: ["deep learning", "neural network", "representation learning"]
    seed_papers: ["Attention Is All You Need", "Deep Residual Learning", "BERT"]
    
  natural_language_processing:
    keywords: ["NLP", "language model", "text generation", "machine translation"]
    seed_papers: ["GPT-3", "BERT", "T5", "InstructGPT"]
    
  computer_vision:
    keywords: ["image recognition", "object detection", "segmentation"]
    seed_papers: ["ResNet", "YOLO", "Vision Transformer", "Stable Diffusion"]
    
  reinforcement_learning:
    keywords: ["reinforcement learning", "policy gradient", "Q-learning"]
    seed_papers: ["AlphaGo", "PPO", "DQN", "RLHF"]
    
  graph_neural_networks:
    keywords: ["graph neural network", "GNN", "graph convolution"]
    seed_papers: ["GCN", "GraphSAGE", "GAT"]
    
  generative_models:
    keywords: ["generative model", "GAN", "diffusion", "VAE"]
    seed_papers: ["GAN", "DDPM", "Stable Diffusion", "Flow Matching"]
    
  systems:
    keywords: ["distributed system", "database", "operating system"]
    seed_papers: ["Raft", "Spanner", "MapReduce"]
    
  security:
    keywords: ["cybersecurity", "adversarial", "privacy"]
    seed_papers: ["Differential Privacy", "Federated Learning"]
```

## 4. 爬取流程

```
┌─────────────────┐
│  种子清单 / 搜索  │
│  关键词配置       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│ Semantic Scholar │────▶│   去重合并    │
│ + OpenAlex 查询  │     │  (按 DOI/标题)│
└─────────────────┘     └──────┬───────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────┐    ┌───────────────┐     ┌───────────────┐
│ 引用量筛选   │    │ 会议/期刊筛选  │     │ SOTA 排名筛选  │
│ (高被引)     │    │ (顶会顶刊)    │     │ (PapersWithCode)│
└──────┬──────┘    └──────┬────────┘     └───────┬───────┘
       │                  │                      │
       └──────────────────┼──────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  候选论文列表    │
                 │  (评分排序)      │
                 └────────┬────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
        ┌──────────┐ ┌─────────┐ ┌──────────┐
        │ 获取详情  │ │下载 PDF │ │ 获取引用  │
        │ (元数据)  │ │ (arXiv) │ │ 关系网络  │
        └─────┬────┘ └────┬────┘ └─────┬────┘
              │           │            │
              └───────────┼────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  入库 + AI 分析  │
                 │  (触发关联发现)   │
                 └─────────────────┘
```

## 5. 技术实现

### 5.1 模块结构

```
backend/app/services/crawlers/
├── __init__.py
├── base.py              # 爬虫基类（限流、重试、日志）
├── semantic_scholar.py  # Semantic Scholar API 爬虫
├── arxiv_crawler.py     # arXiv API 爬虫
├── dblp_crawler.py      # DBLP API 爬虫
├── pwc_crawler.py       # Papers with Code API 爬虫
├── openalex_crawler.py  # OpenAlex API 爬虫
├── orchestrator.py      # 爬取编排器（调度多个爬虫）
├── deduplicator.py      # 去重逻辑
├── scorer.py            # 论文影响力评分
└── seed_config.yaml     # 种子关键词/论文配置
```

### 5.2 爬虫基类设计

```python
class BaseCrawler:
    """所有爬虫的基类，提供限流、重试、日志等通用能力"""
    
    def __init__(self, rate_limit: float, max_retries: int = 3):
        self.rate_limit = rate_limit      # 请求间隔（秒）
        self.max_retries = max_retries
        self.session: httpx.AsyncClient
    
    async def fetch(self, url, params) -> dict:
        """带限流和重试的请求方法"""
        ...
    
    async def search_papers(self, query, filters) -> list[PaperMeta]:
        """搜索论文（子类实现）"""
        raise NotImplementedError
    
    async def get_paper_details(self, paper_id) -> PaperDetail:
        """获取论文详情（子类实现）"""
        raise NotImplementedError
    
    async def get_citations(self, paper_id) -> list[Citation]:
        """获取引用关系（子类实现）"""
        raise NotImplementedError
```

### 5.3 影响力评分算法

```python
def compute_impact_score(paper: PaperMeta) -> float:
    """综合评分，0-100 分"""
    score = 0
    
    # 引用量权重 (40%)
    citation_score = min(paper.citation_count / 1000, 1.0) * 40
    
    # 年均引用增长 (20%)
    years = current_year - paper.year
    annual_citations = paper.citation_count / max(years, 1)
    growth_score = min(annual_citations / 200, 1.0) * 20
    
    # 会议/期刊等级 (20%)
    venue_score = VENUE_RANK.get(paper.venue, 0) * 20
    
    # SOTA 记录 (10%)
    sota_score = min(paper.sota_count / 5, 1.0) * 10
    
    # 有影响力引用比例 (10%)
    influential_ratio = paper.influential_citations / max(paper.citation_count, 1)
    influential_score = min(influential_ratio / 0.1, 1.0) * 10
    
    return citation_score + growth_score + venue_score + sota_score + influential_score
```

### 5.4 限流与礼貌爬取

- 遵守各 API 的 rate limit
- 指数退避重试
- User-Agent 标明项目身份
- 优先使用官方 API，不做网页抓取
- 支持断点续爬（记录已处理 offset）
- 爬取任务通过 Celery 异步执行

## 6. API 接口

### 触发爬取任务
```http
POST /api/v1/crawler/start
Body:
{
  "domain": "computer_science",
  "subdomain": "deep_learning",      // 可选
  "year_from": 2016,
  "year_to": 2026,
  "min_citations": 500,
  "sources": ["semantic_scholar", "openalex"],
  "max_papers": 200,
  "auto_download_pdf": true
}

Response 202:
{
  "task_id": "crawl_task_abc",
  "status": "queued",
  "estimated_papers": "~200"
}
```

### 查看爬取进度
```http
GET /api/v1/crawler/tasks/{task_id}

Response 200:
{
  "task_id": "crawl_task_abc",
  "status": "running",           // queued | running | completed | failed
  "progress": {
    "searched": 1500,
    "candidates": 320,
    "downloaded": 85,
    "imported": 72,
    "failed": 3,
    "deduped": 10
  },
  "started_at": "2026-03-15T10:00:00Z",
  "elapsed": "00:12:34"
}
```

### 预设爬取方案
```http
POST /api/v1/crawler/presets/cs-landmarks

# 一键爬取计算机科学近10年里程碑论文
# 内部逻辑：
#   1. 从种子清单出发
#   2. Semantic Scholar 搜索各子领域 top cited
#   3. 补充 Best Paper Award 列表
#   4. 从 Papers with Code 获取 SOTA 工作
#   5. 综合评分，取 Top-N
```

## 7. 注意事项

- **版权合规**：仅下载 Open Access 论文的 PDF，非 OA 论文只存储元数据
- **存储管理**：PDF 按 `storage/papers/{year}/{paper_id}.pdf` 组织
- **幂等性**：重复爬取同一论文不会产生重复记录（基于 DOI / Semantic Scholar ID 去重）
- **可观测性**：爬取过程全程日志 + 进度上报
