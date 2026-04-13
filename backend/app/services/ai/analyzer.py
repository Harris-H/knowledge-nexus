"""
知识关联分析引擎 — 利用 LLM 发现跨领域知识间的深层关联。
核心能力：
1. 分析两个知识节点/论文之间的潜在关联
2. 从整体知识库中发现新的跨域连接
3. 基于已有关联推导新知识/新假设
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Paper, KnowledgeNode, Relation, gen_id
from app.services.ai.llm_client import chat_completion_json

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
#  Prompt 模板
# ══════════════════════════════════════════════════════════════

DISCOVER_RELATIONS_PROMPT = """你是一个跨领域知识关联专家。你的任务是发现不同领域知识之间隐藏的深层联系。

以下是知识库中的一些知识节点和论文（格式：- 「节点名称」 [类型|领域] 描述）：

{nodes_text}

以下是已经发现的部分关联（避免重复）：
{existing_relations_text}

请分析上述知识，发现 **尚未建立但确实存在** 的跨领域关联。优先发现：
1. 不同领域之间的结构类比（如生物现象→算法）
2. 一个领域的原理/方法在另一个领域的应用
3. 多个领域共享的深层模式（如反馈、优化、涌现）
4. 可能产生新知识或新研究方向的关联

⚠️ 重要：source_name 和 target_name 必须只填「」中的名称，不要包含描述文字！

对每条发现的关联，提供：
- source_name: 源节点名称（必须是上面「」中的名称，原样复制）
- target_name: 目标节点名称（必须是上面「」中的名称，原样复制）
- relation_type: 关系类型（INSPIRES / ANALOGOUS_TO / RELATED_TO / BUILDS_ON）
- description: 详细的中文描述，说明为什么存在这个关联（50-100字）
- confidence: 关联可信度（0.5-1.0）
- insight: 这条关联可能启发什么新知识/新研究？（20-50字）

以 JSON 数组格式返回，发现 5-10 条关联：
```json
[
  {{
    "source_name": "自然选择与进化",
    "target_name": "遗传算法",
    "relation_type": "ANALOGOUS_TO",
    "description": "...",
    "confidence": 0.8,
    "insight": "..."
  }}
]
```"""

DERIVE_KNOWLEDGE_PROMPT = """你是一个跨领域知识推导专家。你的任务是基于已有知识和关联，推导出新的知识、假设或研究方向。

以下是一组相关的知识节点及其关联：

{context_text}

请基于以上知识进行深度分析和推导：

1. **本质抽象**：这些知识的共同深层模式是什么？能否用一个统一的框架/原理来解释？
2. **知识迁移**：某个领域的成功方法/原理，能否迁移到另一个领域？会产生什么新方法？
3. **缺失环节**：这个知识网络中有什么明显的缺失？可能存在但尚未被发现的关联？
4. **新假设**：基于这些关联，能提出什么新的研究假设或实验方向？

以 JSON 格式返回：
```json
{{
  "abstract_pattern": {{
    "name": "模式名称",
    "description": "对共同深层模式的描述（100-200字）"
  }},
  "transfer_ideas": [
    {{
      "from_domain": "源领域",
      "to_domain": "目标领域",
      "idea": "具体的迁移想法（50-100字）",
      "feasibility": "high/medium/low"
    }}
  ],
  "missing_links": [
    {{
      "description": "缺失的关联描述（30-50字）",
      "potential_value": "如果发现这个关联的潜在价值"
    }}
  ],
  "new_hypotheses": [
    {{
      "hypothesis": "新假设内容（50-100字）",
      "evidence_needed": "验证所需的证据/实验",
      "impact": "high/medium/low"
    }}
  ]
}}
```"""

ANALYZE_PAIR_PROMPT = """你是一个跨领域知识关联分析师。请深入分析以下两个知识点之间可能存在的关联：

**知识A**: {node_a_text}

**知识B**: {node_b_text}

请从以下维度进行分析：
1. **结构类比**：两者在结构/机制上有什么相似之处？
2. **因果联系**：一个是否启发/催生了另一个？
3. **互补性**：两者结合能产生什么新价值？
4. **统一框架**：是否存在一个更高层的概念能同时解释两者？

以 JSON 格式返回：
```json
{{
  "has_relation": true/false,
  "relation_type": "ANALOGOUS_TO / INSPIRES / RELATED_TO / BUILDS_ON / NONE",
  "description": "关联描述（50-100字中文）",
  "confidence": 0.0-1.0,
  "structural_analogy": "结构类比说明",
  "causal_link": "因果联系说明",
  "complementarity": "互补性说明",
  "unified_framework": "统一框架说明",
  "new_insight": "可能产生的新知识或启示"
}}
```"""


# ══════════════════════════════════════════════════════════════
#  服务函数
# ══════════════════════════════════════════════════════════════


def _node_to_text(name: str, node_type: str, domain: str, summary: str, description: str) -> str:
    """将知识节点格式化为文本，名称和描述用 | 分隔以便LLM区分"""
    desc = summary or description[:100]
    return f"- 「{name}」 [{node_type}|{domain}] {desc}"


def _fuzzy_match(query: str, name_to_id: dict) -> str | None:
    """模糊匹配节点名称：先精确→再包含→再最长公共子串"""
    query = query.strip()
    if not query:
        return None
    # 精确匹配
    if query in name_to_id:
        return name_to_id[query]
    # query 包含某个 name，或某个 name 包含 query
    best_name, best_len = None, 0
    for name, nid in name_to_id.items():
        if name in query or query in name:
            overlap = min(len(name), len(query))
            if overlap > best_len:
                best_name, best_len = name, overlap
    if best_name:
        return name_to_id[best_name]
    # 去除括号/标点后再试
    import re

    q_clean = re.sub(r"[\s\(\)（）\[\]【】「」:：\-—/]", "", query.lower())
    for name, nid in name_to_id.items():
        n_clean = re.sub(r"[\s\(\)（）\[\]【】「」:：\-—/]", "", name.lower())
        if q_clean == n_clean or q_clean in n_clean or n_clean in q_clean:
            return nid
    return None


async def discover_relations(
    db: AsyncSession, limit: int = 10, domains: list[str] | None = None
) -> dict:
    """
    从知识库中自动发现新的跨领域关联。
    domains: 限定搜索范围的领域列表，None=全部领域。
    """
    # 加载知识节点
    kn_query = select(KnowledgeNode)
    if domains:
        kn_query = kn_query.where(KnowledgeNode.domain.in_(domains))
    kn_result = await db.execute(kn_query)
    kn_nodes = kn_result.scalars().all()

    # 加载所有论文
    paper_result = await db.execute(select(Paper).order_by(Paper.citation_count.desc()).limit(30))
    papers = paper_result.scalars().all()

    # 构建节点文本
    nodes_text_lines = []
    name_to_id = {}
    name_to_type = {}

    for kn in kn_nodes:
        line = _node_to_text(
            kn.name, kn.node_type, kn.domain, kn.summary or "", kn.description or ""
        )
        nodes_text_lines.append(line)
        name_to_id[kn.name] = kn.id
        name_to_type[kn.name] = "knowledge_node"

    for p in papers:
        name = p.key_contributions or p.title
        line = f"- 「{name}」 [paper|computer_science] {p.summary or (p.abstract or '')[:100]}"
        nodes_text_lines.append(line)
        name_to_id[name] = p.id
        name_to_type[name] = "paper"
        # 也用标题索引
        if p.key_contributions:
            name_to_id[p.title] = p.id
            name_to_type[p.title] = "paper"

    # 加载已有关系
    rel_result = await db.execute(select(Relation))
    existing_rels = rel_result.scalars().all()

    existing_text_lines = []
    existing_pairs = set()
    for r in existing_rels:
        existing_pairs.add((r.source_id, r.target_id))
        desc = (r.description or "")[:50]
        existing_text_lines.append(f"{r.relation_type}: {desc}")

    nodes_text = "\n".join(nodes_text_lines)
    existing_relations_text = "\n".join(existing_text_lines[:30])

    # 调用 LLM
    prompt = DISCOVER_RELATIONS_PROMPT.format(
        nodes_text=nodes_text,
        existing_relations_text=existing_relations_text or "（暂无）",
    )

    result = await chat_completion_json(
        [
            {
                "role": "system",
                "content": "你是跨领域知识关联发现专家。请严格按照JSON格式返回结果。"
                "注意：source_name 和 target_name 必须只填节点名称（即「」中的内容），"
                "不要包含描述文字。",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    # 解析并匹配 ID
    discoveries = []
    if isinstance(result, list):
        items = result
    elif isinstance(result, dict) and "relations" in result:
        items = result["relations"]
    else:
        items = result if isinstance(result, list) else []

    for item in items[:limit]:
        src_name = item.get("source_name", "")
        tgt_name = item.get("target_name", "")
        src_id = _fuzzy_match(src_name, name_to_id)
        tgt_id = _fuzzy_match(tgt_name, name_to_id)

        if not src_id or not tgt_id:
            logger.warning(f"⚠ 无法匹配: {src_name} -> {tgt_name}")
            continue
        if (src_id, tgt_id) in existing_pairs:
            logger.info(f"⏭ 已存在: {src_name} -> {tgt_name}")
            continue

        # 反查匹配到的实际名称
        src_real = next((n for n, i in name_to_id.items() if i == src_id), src_name)
        tgt_real = next((n for n, i in name_to_id.items() if i == tgt_id), tgt_name)

        discoveries.append(
            {
                "source_id": src_id,
                "source_name": src_real,
                "source_type": name_to_type.get(src_real, "knowledge_node"),
                "target_id": tgt_id,
                "target_name": tgt_real,
                "target_type": name_to_type.get(tgt_real, "knowledge_node"),
                "relation_type": item.get("relation_type", "RELATED_TO"),
                "description": item.get("description", ""),
                "confidence": item.get("confidence", 0.7),
                "insight": item.get("insight", ""),
            }
        )

    logger.info(f"🔍 发现 {len(discoveries)} 条新关联")
    return {"discoveries": discoveries, "total_nodes": len(nodes_text_lines)}


async def derive_knowledge(db: AsyncSession, node_ids: list[str]) -> dict:
    """
    对指定的一组知识节点进行深度推导，产生新知识。
    """
    context_lines = []

    for nid in node_ids:
        # 查知识节点
        result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.id == nid))
        kn = result.scalar_one_or_none()
        if kn:
            context_lines.append(
                f"[{kn.node_type}|{kn.domain}] {kn.name}\n"
                f"  简介: {kn.summary or ''}\n"
                f"  描述: {kn.description or ''}\n"
            )
            continue

        # 查论文
        result = await db.execute(select(Paper).where(Paper.id == nid))
        paper = result.scalar_one_or_none()
        if paper:
            context_lines.append(
                f"[paper] {paper.key_contributions or paper.title}\n"
                f"  简介: {paper.summary or ''}\n"
                f"  摘要: {(paper.abstract or '')[:200]}\n"
            )

    # 加载这些节点间的关系
    rel_result = await db.execute(
        select(Relation).where(
            Relation.source_id.in_(node_ids) | Relation.target_id.in_(node_ids),
            Relation.status == "confirmed",
        )
    )
    rels = rel_result.scalars().all()
    for r in rels:
        context_lines.append(f"关联: {r.relation_type} — {r.description or ''}")

    context_text = "\n".join(context_lines)

    prompt = DERIVE_KNOWLEDGE_PROMPT.format(context_text=context_text)

    result = await chat_completion_json(
        [
            {
                "role": "system",
                "content": "你是跨领域知识推导专家。请严格按照JSON格式返回深度分析结果。",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return result


async def analyze_pair(db: AsyncSession, node_a_id: str, node_b_id: str) -> dict:
    """
    深度分析两个知识节点之间的关联。
    """

    async def get_node_text(nid: str) -> str:
        result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.id == nid))
        kn = result.scalar_one_or_none()
        if kn:
            return (
                f"名称: {kn.name}\n类型: {kn.node_type}\n领域: {kn.domain}\n"
                f"简介: {kn.summary or ''}\n描述: {kn.description or ''}"
            )
        result = await db.execute(select(Paper).where(Paper.id == nid))
        paper = result.scalar_one_or_none()
        if paper:
            return (
                f"名称: {paper.key_contributions or paper.title}\n类型: paper\n领域: computer_science\n"
                f"简介: {paper.summary or ''}\n摘要: {(paper.abstract or '')[:300]}"
            )
        return "未找到"

    node_a_text = await get_node_text(node_a_id)
    node_b_text = await get_node_text(node_b_id)

    prompt = ANALYZE_PAIR_PROMPT.format(
        node_a_text=node_a_text,
        node_b_text=node_b_text,
    )

    result = await chat_completion_json(
        [
            {
                "role": "system",
                "content": "你是跨领域知识关联分析师。请严格按照JSON格式返回分析结果。",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=1500,
    )

    return result


async def save_discovered_relations(
    db: AsyncSession,
    discoveries: list[dict],
    auto_confirm: bool = False,
) -> int:
    """
    将 AI 发现的关联保存到数据库。
    auto_confirm=False 时保存为 pending 状态，等待人工审核。
    """
    saved = 0
    for d in discoveries:
        relation = Relation(
            id=gen_id(),
            source_id=d["source_id"],
            source_type=d.get("source_type", "knowledge_node"),
            target_id=d["target_id"],
            target_type=d.get("target_type", "knowledge_node"),
            relation_type=d.get("relation_type", "RELATED_TO"),
            description=d.get("description", ""),
            confidence=d.get("confidence", 0.7),
            ai_generated=True,
            status="confirmed" if auto_confirm else "pending",
        )
        db.add(relation)
        saved += 1

    await db.flush()
    logger.info(
        f"💾 保存 {saved} 条 AI 发现的关联 (status={'confirmed' if auto_confirm else 'pending'})"
    )
    return saved
