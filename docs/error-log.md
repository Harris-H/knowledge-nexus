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
