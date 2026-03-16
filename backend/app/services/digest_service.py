"""
领域摘要服务 — 为每个子领域生成 Markdown 格式的知识图谱摘要。

核心能力：
1. 汇总领域内所有知识节点、论文、已有关联，生成结构化摘要
2. 基于两个领域摘要进行快速跨域关联分析
3. 摘要过期管理（数据变更时标记为 stale）
"""
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.models import Domain, KnowledgeNode, Paper, Relation, gen_id
from app.services.ai.llm_client import chat_completion, chat_completion_json

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
#  Prompt 模板
# ══════════════════════════════════════════════════════════════

GENERATE_DIGEST_PROMPT = """你是一个知识图谱摘要专家。请为以下领域生成一份结构化的知识图谱摘要。

## 领域：{domain_name}

### 该领域的知识节点（共 {node_count} 个）：
{nodes_text}

### 该领域相关的论文（共 {paper_count} 篇）：
{papers_text}

### 该领域与其他领域的已有关联（共 {relation_count} 条）：
{relations_text}

---

请生成一份 Markdown 格式的领域摘要，要求：

1. **核心概念清单**：列出该领域最重要的概念/知识点（每个用一句话描述其本质）
2. **关键模式与规律**：提炼该领域反复出现的深层模式（如反馈机制、涌现现象、优化策略等）
3. **方法论特征**：该领域典型的研究方法、解决问题的范式
4. **跨域连接点**：该领域中哪些概念/方法最有可能与其他领域产生关联，以及已知的跨域连接
5. **领域统计**：知识节点数、论文数、已建立关联数

摘要应该：
- 简洁但信息密度高（控制在 800-1500 字）
- 突出「可迁移」的知识模式（方便 AI 做跨域类比）
- 使用清晰的 Markdown 层级结构

直接输出 Markdown 内容，不要用 ```markdown``` 包裹。"""

CROSS_DOMAIN_ANALYSIS_PROMPT = """你是一个跨领域知识关联分析专家。请基于以下两个领域的知识摘要，发现它们之间的深层关联。

## 领域 A 摘要：
{digest_a}

## 领域 B 摘要：
{digest_b}

---

请从以下维度进行深度分析：

1. **结构类比**（analogies）：两个领域中存在结构/机制上相似的概念或现象
2. **知识迁移**（transfer_ideas）：一个领域的方法/原理可以迁移到另一个领域的具体想法
3. **新假设**（new_hypotheses）：基于两个领域的关联，可以提出的新研究假设
4. **统一模式**（unified_patterns）：两个领域共享的深层模式或原理
5. **总结**（summary）：用 2-3 句话概括这两个领域之间最核心的关联

以 JSON 格式返回：
```json
{{
  "analogies": [
    {{
      "concept_a": "领域A中的概念",
      "concept_b": "领域B中的概念",
      "description": "类比说明（50-100字）",
      "depth": "surface / structural / deep"
    }}
  ],
  "transfer_ideas": [
    {{
      "from_domain": "源领域",
      "to_domain": "目标领域",
      "source_method": "源方法/原理",
      "target_application": "目标应用场景",
      "idea": "迁移想法（50-100字）",
      "feasibility": "high / medium / low"
    }}
  ],
  "new_hypotheses": [
    {{
      "hypothesis": "假设内容（50-100字）",
      "basis": "推理依据",
      "impact": "high / medium / low"
    }}
  ],
  "unified_patterns": [
    {{
      "pattern_name": "模式名称",
      "description": "模式描述（50-100字）",
      "in_domain_a": "在领域A中的体现",
      "in_domain_b": "在领域B中的体现"
    }}
  ],
  "summary": "总结（100-200字）"
}}
```"""


# ══════════════════════════════════════════════════════════════
#  辅助函数
# ══════════════════════════════════════════════════════════════

def _normalize_domain(fields_of_study: str | None) -> str:
    """将论文的 fields_of_study 归一化为 domain 字符串"""
    from app.api.graph import _normalize_paper_domain
    return _normalize_paper_domain(fields_of_study)


async def _ensure_domain_exists(db: AsyncSession, domain_name: str) -> Domain:
    """确保 Domain 记录存在，不存在则创建"""
    result = await db.execute(
        select(Domain).where(Domain.name == domain_name)
    )
    domain = result.scalar_one_or_none()
    if not domain:
        domain = Domain(id=gen_id(), name=domain_name)
        db.add(domain)
        await db.flush()
        logger.info(f"📁 自动创建领域: {domain_name}")
    return domain


async def _get_domain_nodes(db: AsyncSession, domain_name: str) -> list[KnowledgeNode]:
    """获取领域内的所有知识节点"""
    result = await db.execute(
        select(KnowledgeNode).where(KnowledgeNode.domain == domain_name)
    )
    return list(result.scalars().all())


async def _get_domain_papers(db: AsyncSession, domain_name: str) -> list[Paper]:
    """获取领域相关的论文"""
    result = await db.execute(select(Paper))
    papers = result.scalars().all()
    return [p for p in papers if _normalize_domain(p.fields_of_study) == domain_name]


async def _get_domain_relations(
    db: AsyncSession, node_ids: set[str]
) -> list[Relation]:
    """获取涉及指定节点的已确认关联"""
    if not node_ids:
        return []
    result = await db.execute(
        select(Relation).where(
            (Relation.source_id.in_(node_ids) | Relation.target_id.in_(node_ids)),
            Relation.status == "confirmed",
        )
    )
    return list(result.scalars().all())


# ══════════════════════════════════════════════════════════════
#  核心服务
# ══════════════════════════════════════════════════════════════

async def generate_domain_digest(db: AsyncSession, domain_name: str) -> Domain:
    """
    为指定领域生成 Markdown 格式的知识图谱摘要。
    如果领域不存在则自动创建。
    """
    domain = await _ensure_domain_exists(db, domain_name)

    # 收集领域数据
    kn_nodes = await _get_domain_nodes(db, domain_name)
    papers = await _get_domain_papers(db, domain_name)

    all_ids = {kn.id for kn in kn_nodes} | {p.id for p in papers}
    relations = await _get_domain_relations(db, all_ids)

    # 构建文本
    nodes_text_lines = []
    for kn in kn_nodes:
        desc = kn.summary or (kn.description or "")[:120]
        nodes_text_lines.append(f"- **{kn.name}** [{kn.node_type}] {desc}")
    nodes_text = "\n".join(nodes_text_lines) if nodes_text_lines else "（暂无知识节点）"

    papers_text_lines = []
    for p in papers:
        name = p.key_contributions or p.title
        desc = p.summary or (p.abstract or "")[:120]
        cite = f"引用:{p.citation_count}" if p.citation_count else ""
        papers_text_lines.append(f"- **{name}** {cite} {desc}")
    papers_text = "\n".join(papers_text_lines) if papers_text_lines else "（暂无论文）"

    relations_text_lines = []
    for r in relations:
        desc = (r.description or "")[:80]
        relations_text_lines.append(f"- [{r.relation_type}] {desc}")
    relations_text = "\n".join(relations_text_lines) if relations_text_lines else "（暂无关联）"

    # 调用 LLM 生成摘要
    prompt = GENERATE_DIGEST_PROMPT.format(
        domain_name=domain_name,
        node_count=len(kn_nodes),
        paper_count=len(papers),
        nodes_text=nodes_text,
        papers_text=papers_text,
        relation_count=len(relations),
        relations_text=relations_text,
    )

    digest_md = await chat_completion(
        messages=[
            {"role": "system", "content": "你是知识图谱摘要专家。请生成简洁、信息密度高的领域摘要。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=3000,
    )

    # 更新 Domain 记录
    domain.digest_markdown = digest_md
    domain.digest_version = (domain.digest_version or 0) + 1
    domain.digest_node_count = len(kn_nodes)
    domain.digest_paper_count = len(papers)
    domain.digest_relation_count = len(relations)
    domain.digest_generated_at = datetime.utcnow()
    domain.digest_is_stale = False

    await db.flush()
    logger.info(
        f"📝 领域摘要已生成: {domain_name} "
        f"(v{domain.digest_version}, {len(kn_nodes)}节点, {len(papers)}论文, {len(relations)}关联)"
    )
    return domain


async def get_or_generate_digest(db: AsyncSession, domain_name: str) -> Domain:
    """获取领域摘要，如果不存在或已过期则重新生成"""
    result = await db.execute(
        select(Domain).where(Domain.name == domain_name)
    )
    domain = result.scalar_one_or_none()

    if domain and domain.digest_markdown and not domain.digest_is_stale:
        return domain

    return await generate_domain_digest(db, domain_name)


async def regenerate_all_digests(db: AsyncSession) -> list[dict]:
    """重新生成所有领域的摘要"""
    # 收集所有 domain 名称（来自 KnowledgeNode + Paper）
    domain_names = set()

    kn_result = await db.execute(
        select(KnowledgeNode.domain).distinct()
    )
    for row in kn_result:
        domain_names.add(row[0])

    paper_result = await db.execute(select(Paper))
    for p in paper_result.scalars().all():
        domain_names.add(_normalize_domain(p.fields_of_study))

    results = []
    for name in sorted(domain_names):
        try:
            domain = await generate_domain_digest(db, name)
            results.append({
                "domain": name,
                "status": "ok",
                "version": domain.digest_version,
            })
        except Exception as e:
            logger.error(f"❌ 生成 {name} 摘要失败: {e}")
            results.append({"domain": name, "status": "error", "error": str(e)})

    return results


async def cross_domain_analysis(
    db: AsyncSession, domain_a: str, domain_b: str
) -> dict:
    """
    基于两个领域的摘要进行跨域关联分析。
    如果摘要不存在则先生成。
    """
    # 获取或生成两个领域的摘要
    domain_a_obj = await get_or_generate_digest(db, domain_a)
    domain_b_obj = await get_or_generate_digest(db, domain_b)

    digest_a = domain_a_obj.digest_markdown or "（空摘要）"
    digest_b = domain_b_obj.digest_markdown or "（空摘要）"

    prompt = CROSS_DOMAIN_ANALYSIS_PROMPT.format(
        digest_a=digest_a,
        digest_b=digest_b,
    )

    result = await chat_completion_json(
        messages=[
            {"role": "system", "content": "你是跨领域知识关联分析专家。请严格按照 JSON 格式返回分析结果。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=3000,
    )

    # 补充元信息
    result["domain_a"] = domain_a
    result["domain_b"] = domain_b

    logger.info(f"🔗 跨域分析完成: {domain_a} ↔ {domain_b}")
    return result


async def mark_domain_digest_stale(db: AsyncSession, domain_name: str) -> None:
    """标记领域摘要为过期（当领域数据变更时调用）"""
    result = await db.execute(
        select(Domain).where(Domain.name == domain_name)
    )
    domain = result.scalar_one_or_none()
    if domain and domain.digest_markdown:
        domain.digest_is_stale = True
        await db.flush()
        logger.info(f"⚠️ 领域摘要已标记过期: {domain_name}")


async def list_all_domains_with_digest(db: AsyncSession) -> list[Domain]:
    """列出所有有数据的领域（包含摘要状态）"""
    # 从 KnowledgeNode 和 Paper 收集所有 domain
    domain_names = set()

    kn_result = await db.execute(select(KnowledgeNode.domain).distinct())
    for row in kn_result:
        domain_names.add(row[0])

    paper_result = await db.execute(select(Paper))
    for p in paper_result.scalars().all():
        domain_names.add(_normalize_domain(p.fields_of_study))

    # 确保每个 domain 在 Domain 表中都有记录
    domains = []
    for name in sorted(domain_names):
        domain = await _ensure_domain_exists(db, name)
        domains.append(domain)

    return domains
