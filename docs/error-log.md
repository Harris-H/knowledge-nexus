# 错误记录与修复日志

## Issue #1: 前端 API 请求地址硬编码导致连接失败

**现象**
- 图谱页面显示"无符合条件的节点"
- 知识节点页面显示"加载知识节点失败"
- 浏览器控制台报错: `GET http://127.0.0.1:8081/api/v1/graph/full net::ERR_CONNECTION_REFUSED`

**根因**
`frontend/src/api/index.ts` 第 3 行 API 基础路径写死了端口 8081：
```ts
// ❌ 硬编码绝对地址，端口不匹配且绕过了 Vite proxy
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8081/api/v1";
```
实际后端运行在 8082 端口，且 Vite 已配置了 proxy（`vite.config.ts` 中 `/api` → `http://127.0.0.1:8082`），但前端直连 8081 完全绕过了 proxy。

**修复**
```ts
// ✅ 使用相对路径，通过 Vite proxy 转发
const API_BASE = import.meta.env.VITE_API_BASE || "/api/v1";
```

**教训**
- 开发环境应使用相对路径 + Vite proxy，而非硬编码绝对地址
- 绝对地址在端口变化时会静默失败
- 之前测试 API 用的是 `Invoke-RestMethod` 直接命中后端，没有经过前端代码路径，所以没发现问题

---

## Issue #2: AI 发现页面领域下拉框为空

**现象**
AI 发现页面的领域选择下拉框为空。

**根因**
`/ai/nodes` 端点返回的 `domain_counts` 包含混合大小写的 key：
- 知识节点用小写: `"computer_science"`, `"biology"`
- 论文的 `fields_of_study` 从 OpenAlex 导入时为标题格式: `"Computer Science"`, `"Biology"`

前端在解析 domain_counts 时遇到不在预定义列表中的 key，导致渲染为空。

**修复**
后端需统一 domain 命名格式（待完善）；前端已添加 `console.error` 日志。

**教训**
- 数据源（OpenAlex）的命名约定与内部系统不一致时，需在导入层统一格式化

---

## Issue #3: Elite Crawl 启动失败 — DB Schema 过时

**日期**: 2026-04-13

**现象**
- 前端精英爬取点击启动后显示"启动失败"
- 后端返回 HTTP 500 Internal Server Error

**排查过程**
1. 重启后端获取干净日志
2. 用 PowerShell `Invoke-WebRequest -NoProxy` 直接调 API，确认 500 不是前端问题
3. 后端 traceback 定位到关键信息：
   ```
   sqlite3.OperationalError: table crawl_tasks has no column named mode
   ```

**根因**
模型文件 `app/models/models.py` 新增了 `mode`、`author_id`、`institution_id`、`preset_name` 四列，
但项目不使用 Alembic 等迁移工具，SQLite 数据库文件 (`knowledge_nexus.db`) 的表结构停留在旧版本。

SQLAlchemy 的 `create_all()` 只在表不存在时建表，不会自动 ALTER TABLE 补列。

**修复**
1. 手动 `ALTER TABLE crawl_tasks ADD COLUMN ...` 补齐 4 列
2. 新增 `_ensure_crawl_tasks_schema()` 启动检查函数：
   - 服务启动时用 `PRAGMA table_info(crawl_tasks)` 检查列是否存在
   - 缺失则自动 ALTER TABLE 补齐
   - 后续新增字段只需更新 `_CRAWL_TASKS_EXPECTED_COLUMNS` 字典
3. `start_crawl` 端点增加 try/catch，DB 异常不再返回裸 500

**教训**
- 无迁移工具的 SQLite 项目，模型改动后 **必须** 有配套的 schema 检查/迁移逻辑
- API 端点的 DB 操作应 catch 异常并返回结构化错误，而非暴露 500 + 空 body
- 考虑引入 Alembic 做正式迁移管理

---

## Issue #4: OpenAlex 机构/学者 ID 全部错误 — 爬到生物论文

**日期**: 2026-04-13

**现象**
- `top_ai_labs` 预设（Google DeepMind / OpenAI / Meta AI / Microsoft Research）爬取到的论文全是生物学领域
- 如"The 2021 WHO catalogue of Mycobacterium tuberculosis complex mutations"
- 94 篇论文中有 49 篇是生物相关

**排查过程**
1. 爬取结果字段 `fields_of_study` 明显不对（Biology / Genetics / Pathology）
2. 用 OpenAlex API 逐一验证 YAML 中的机构 ID：
   ```
   I1303153112 (标注: Google DeepMind) → 实际: European Bioinformatics Institute
   I2778813966 (标注: OpenAI)          → 实际: 404 Not Found
   I4210108722 (标注: Meta AI)         → 实际: Student Assistance Services
   I1334687557 (标注: Microsoft Research) → 实际: 404 Not Found
   ```
3. 进一步验证发现 **18 个机构 ID 中只有 2 个正确**（Stanford、MIT）
4. **11 个学者 ID 中只有 1 个正确**（Li Fei-Fei）

**根因**
`elite_profiles.yaml` 中的 OpenAlex ID 是由 AI（上一版本的 Copilot）编造的，而非从 OpenAlex API 查询获得。
OpenAlex 的 ID 是不透明的数字标识符（如 `I4210090411`），无法从机构名称推导，只能通过 API 搜索获取。

AI 在缺乏 API 访问的情况下"编造"了看起来合理的 ID，但几乎全部指向了错误的实体。

**修复**
通过 `https://api.openalex.org/institutions?search={name}` 和 `authors?search={name}`
逐一查询并替换了所有 ID：

| 实体 | 旧 ID | 新 ID | 实际指向 |
|------|-------|-------|---------|
| Google DeepMind | I1303153112 | I4210090411 | ✅ Google DeepMind (UK) |
| OpenAI | I2778813966 | I4210161460 | ✅ OpenAI (US) |
| Meta AI | I4210108722 | I4210114444 | ✅ Meta (US) |
| Microsoft Research | I1334687557 | I4210164937 | ✅ Microsoft Research (UK) |
| Carnegie Mellon | I130769515 | I74973139 | ✅ Carnegie Mellon University |
| UC Berkeley | I136199984 | I95457486 | ✅ University of California, Berkeley |
| Geoffrey Hinton | A5048491430 | A5108093963 | ✅ Geoffrey E. Hinton |
| Yoshua Bengio | A5073272612 | A5086198262 | ✅ Yoshua Bengio |
| Yann LeCun | A5014726161 | A5001226970 | ✅ Yann LeCun |
| ... | ... | ... | (共修正 15 机构 + 10 学者) |

**教训**
- **永远不要信任 AI 生成的外部系统 ID** — 必须通过 API 验证
- OpenAlex ID 是不透明标识符，不可能从名称推导出来
- 应在 YAML 中注明"已于 YYYY-MM 通过 API 验证"的标记
- 新增 ID 时建立 checklist：编辑 → API 验证 → 填入 → 测试爬取结果的领域是否匹配

---

## Issue #5: 论文列表排序无效 — 客户端排序 vs 服务端分页冲突

**日期**: 2026-04-13 ~ 2026-04-14

**现象**
- 论文列表新增"入库时间"列后，点击列头排序无效果
- 所有可排序列（评分、引用、入库时间）的排序表现异常

**排查过程**
1. 检查前端 `sorter` 回调函数逻辑 — 语法正确
2. 检查 `created_at` 数据格式 — API 返回 `2026-03-15T04:16:37.484579`（ISO 8601），`new Date()` 可正确解析
3. 检查数据分布 — 确实有两个不同日期（3/15 和 4/13），排序应可见差异
4. **发现根因**：Table 使用 **服务端分页**（每页 20 条，API 返回 total），但排序用 **客户端 sorter**

**根因**
Ant Design Table 的 `sorter: (a, b) => ...` 是 **纯客户端排序**，只对当前页的 20 条数据排序。
而论文列表是 **服务端分页**（API 带 `page` + `size` 参数），总共 94 篇论文分 5 页。

这导致：
- 客户端排序只能在当前页 20 条数据内重排
- 如果最新入库的论文在第 1 页和第 5 页各有分布，排序看起来"没效果"
- `defaultSortOrder: "descend"` 在引用列上还会与其他列的排序互相冲突

此外，Store 层硬编码了 `sort: "citation_count"`，忽略用户在 UI 选择的排序列。

**修复**
改为 **完整的服务端排序**：

1. **后端**：`/api/v1/papers/` 新增 `order` 参数（`asc` | `desc`）
   ```python
   sort_col = getattr(Paper, sort, Paper.impact_score)
   query = query.order_by(sort_col.asc() if order == "asc" else sort_col.desc())
   ```

2. **Store**：新增 `paperSort` 状态 + `setPaperSort` action，`fetchPapers` 动态传入 sort/order

3. **前端**：
   - 列定义改为 `sorter: true`（声明可排序但不做客户端排序）
   - Table `onChange` 回调捕获排序变化，调用 `setPaperSort` + 重新 fetch
   - `useEffect` 依赖加入 `paperSort`

**教训**
- **分页模式必须与排序模式一致**：服务端分页 → 服务端排序，客户端分页 → 客户端排序
- Ant Design 的 `sorter: (a, b) => ...` 只适用于全量数据在前端的场景
- 服务端排序应使用 `sorter: true` + `onChange` 回调
- 这是一个常见的 Ant Design 误用模式，尤其在从全量加载改为分页加载时容易遗漏
