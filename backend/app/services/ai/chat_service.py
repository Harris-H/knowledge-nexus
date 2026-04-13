"""
AI 对话服务 — 对话式知识发现界面的后端编排层。

用户输入自然语言 → LLM 判断意图并提取参数 → 调用对应内部服务 → 返回结构化结果。

支持的技能(Skills)：
  - search_knowledge: 搜索知识库
  - discover_relations: 发现跨领域关联
  - analyze_pair: 深度分析两个节点
  - derive_knowledge: 推导新知识
  - get_domain_digest: 获取/生成领域摘要
  - cross_domain_analysis: 跨域关联分析
  - list_domains: 列出所有领域
  - general_chat: 通用问答（无需调用内部服务）
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import KnowledgeNode, Paper
from app.services.ai.llm_client import chat_completion, chat_completion_json
from app.services.ai.analyzer import (
    discover_relations,
    derive_knowledge,
    analyze_pair,
)
from app.services.digest_service import (
    generate_domain_digest,
    cross_domain_analysis,
    list_all_domains_with_digest,
)

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
#  技能路由系统提示
# ══════════════════════════════════════════════════════════════

ROUTER_SYSTEM_PROMPT = """你是 Knowledge Nexus 的 AI 助手，一个跨领域知识关联引擎。
你可以调用以下技能来帮助用户：

## 可用技能

1. **search_knowledge** — 搜索知识库中的论文和知识节点
   参数: {"query": "搜索关键词"}

2. **discover_relations** — 在知识库中发现新的跨领域关联
   参数: {"limit": 数量(默认5), "domains": ["领域1", "领域2"](可选)}
   领域可选值: computer_science, speech_ai, biology, physics, mathematics, neuroscience, chemistry, engineering, psychology, ecology, philosophy, sociology, economics, art, cognitive_science, history, life_science, medicine, military_science

3. **analyze_pair** — 深度分析两个知识概念之间的关联
   参数: {"node_a_name": "概念A名称", "node_b_name": "概念B名称"}

4. **derive_knowledge** — 基于一组知识概念推导新知识
   参数: {"node_names": ["概念1", "概念2", ...]}

5. **get_domain_digest** — 获取或生成某个领域的知识摘要
   参数: {"domain": "领域名称"}

6. **cross_domain_analysis** — 分析两个领域之间的跨域关联
   参数: {"domain_a": "领域A", "domain_b": "领域B"}

7. **list_domains** — 列出所有可用领域及统计信息
   参数: {}

8. **general_chat** — 通用回答，不需要调用任何技能
   参数: {}

## 规则
- 根据用户的自然语言输入，判断应该调用哪个技能
- 如果用户的问题可以直接回答（如打招呼、问你是谁），使用 general_chat
- 如果用户提到具体的领域名称，将其转换为英文 key（如"计算机"→"computer_science"，"生物学"→"biology"）
- 如果用户提到两个具体概念，优先使用 analyze_pair
- 如果用户想了解某个领域的整体情况，使用 get_domain_digest
- 如果用户想比较/关联两个领域，使用 cross_domain_analysis

请以 JSON 格式返回你的决策：
```json
{
  "skill": "技能名称",
  "params": {参数},
  "reply_prefix": "一句简短的过渡语，告诉用户你正在做什么"
}
```"""

DOMAIN_ZH_TO_EN = {
    "计算机": "computer_science",
    "计算机科学": "computer_science",
    "CS": "computer_science",
    "语音": "speech_ai",
    "语音AI": "speech_ai",
    "语音识别": "speech_ai",
    "生物": "biology",
    "生物学": "biology",
    "物理": "physics",
    "物理学": "physics",
    "数学": "mathematics",
    "数学学": "mathematics",
    "神经科学": "neuroscience",
    "脑科学": "neuroscience",
    "化学": "chemistry",
    "工程": "engineering",
    "工程学": "engineering",
    "心理学": "psychology",
    "心理": "psychology",
    "生态": "ecology",
    "生态学": "ecology",
    "哲学": "philosophy",
    "社会学": "sociology",
    "社会": "sociology",
    "经济": "economics",
    "经济学": "economics",
    "艺术": "art",
    "认知科学": "cognitive_science",
    "认知": "cognitive_science",
    "历史": "history",
    "历史学": "history",
    "生命科学": "life_science",
    "医学": "medicine",
    "医": "medicine",
    "军事": "military_science",
    "军事学": "military_science",
}

DOMAIN_LABELS = {
    "computer_science": "💻 计算机",
    "speech_ai": "🎤 语音AI",
    "biology": "🧬 生物学",
    "physics": "⚛️ 物理学",
    "mathematics": "📊 数学",
    "neuroscience": "🧠 神经科学",
    "chemistry": "🧪 化学",
    "engineering": "⚙️ 工程学",
    "psychology": "🧠 心理学",
    "ecology": "🌍 生态学",
    "philosophy": "🤔 哲学",
    "sociology": "👥 社会学",
    "economics": "📈 经济学",
    "art": "🎨 艺术",
    "cognitive_science": "🧩 认知科学",
    "history": "📜 历史",
    "life_science": "🔬 生命科学",
    "medicine": "🏥 医学",
    "military_science": "🎖️ 军事学",
}


# ══════════════════════════════════════════════════════════════
#  辅助函数
# ══════════════════════════════════════════════════════════════


async def _find_node_by_name(db: AsyncSession, name: str) -> dict | None:
    """通过名称模糊匹配知识节点或论文"""
    # 精确匹配知识节点
    result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.name == name))
    kn = result.scalar_one_or_none()
    if kn:
        return {"id": kn.id, "name": kn.name, "type": "knowledge_node"}

    # 模糊匹配知识节点
    result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.name.ilike(f"%{name}%")))
    kn = result.scalars().first()
    if kn:
        return {"id": kn.id, "name": kn.name, "type": "knowledge_node"}

    # 模糊匹配论文
    result = await db.execute(
        select(Paper).where(
            Paper.title.ilike(f"%{name}%") | Paper.key_contributions.ilike(f"%{name}%")
        )
    )
    paper = result.scalars().first()
    if paper:
        return {
            "id": paper.id,
            "name": paper.key_contributions or paper.title,
            "type": "paper",
        }

    return None


async def _search_knowledge(db: AsyncSession, query: str) -> dict:
    """搜索知识库"""
    items = []

    # 搜索知识节点
    result = await db.execute(
        select(KnowledgeNode)
        .where(
            KnowledgeNode.name.ilike(f"%{query}%")
            | KnowledgeNode.description.ilike(f"%{query}%")
            | KnowledgeNode.summary.ilike(f"%{query}%")
        )
        .limit(10)
    )
    for kn in result.scalars().all():
        items.append(
            {
                "id": kn.id,
                "name": kn.name,
                "type": "knowledge_node",
                "domain": kn.domain,
                "node_type": kn.node_type,
                "summary": kn.summary or (kn.description or "")[:150],
            }
        )

    # 搜索论文
    result = await db.execute(
        select(Paper)
        .where(
            Paper.title.ilike(f"%{query}%")
            | Paper.abstract.ilike(f"%{query}%")
            | Paper.key_contributions.ilike(f"%{query}%")
        )
        .limit(10)
    )
    for p in result.scalars().all():
        items.append(
            {
                "id": p.id,
                "name": p.key_contributions or p.title,
                "type": "paper",
                "domain": p.fields_of_study or "",
                "node_type": "paper",
                "summary": p.summary or (p.abstract or "")[:150],
            }
        )

    return {"items": items, "total": len(items), "query": query}


# ══════════════════════════════════════════════════════════════
#  核心对话处理
# ══════════════════════════════════════════════════════════════


async def process_chat(
    db: AsyncSession,
    messages: list[dict],
) -> dict:
    """
    处理对话消息，返回 AI 响应。

    流程: 用户消息 → LLM 意图识别 → 调用技能 → 生成响应

    Returns:
        {
            "role": "assistant",
            "content": "自然语言回复（Markdown）",
            "skill_used": "技能名称" | None,
            "structured_data": {"type": "...", "data": {...}} | None
        }
    """
    # Step 1: LLM 意图识别 — 决定调用哪个技能
    router_messages = [
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        *[
            {"role": m["role"], "content": m["content"]} for m in messages[-6:]
        ],  # 保留最近 6 条上下文
    ]

    try:
        decision = await chat_completion_json(
            messages=router_messages,
            temperature=0.1,
            max_tokens=500,
        )
    except Exception as e:
        logger.error(f"❌ 意图识别失败: {e}")
        return {
            "role": "assistant",
            "content": "抱歉，我暂时无法理解您的请求。请尝试更具体地描述您想做什么。",
            "skill_used": None,
            "structured_data": None,
        }

    skill = decision.get("skill", "general_chat")
    params = decision.get("params", {})
    reply_prefix = decision.get("reply_prefix", "")

    logger.info(f"🎯 意图识别: skill={skill}, params={params}")

    # Step 2: 执行技能
    try:
        result = await _execute_skill(db, skill, params)
    except Exception as e:
        logger.error(f"❌ 技能执行失败 [{skill}]: {e}")
        return {
            "role": "assistant",
            "content": f"{reply_prefix}\n\n抱歉，执行过程中出现错误: {str(e)}",
            "skill_used": skill,
            "structured_data": None,
        }

    # Step 3: 生成自然语言总结
    content = await _generate_summary(skill, params, result, reply_prefix, messages)

    return {
        "role": "assistant",
        "content": content,
        "skill_used": skill,
        "structured_data": result,
    }


async def _execute_skill(db: AsyncSession, skill: str, params: dict) -> dict | None:
    """根据技能名称调用对应的后端服务"""

    if skill == "general_chat":
        return None

    elif skill == "search_knowledge":
        query = params.get("query", "")
        if not query:
            return None
        return {
            "type": "search_results",
            "data": await _search_knowledge(db, query),
        }

    elif skill == "discover_relations":
        limit = params.get("limit", 5)
        domains = params.get("domains")
        result = await discover_relations(db, limit=limit, domains=domains)
        return {
            "type": "discoveries",
            "data": result,
        }

    elif skill == "analyze_pair":
        name_a = params.get("node_a_name", "")
        name_b = params.get("node_b_name", "")
        node_a = await _find_node_by_name(db, name_a)
        node_b = await _find_node_by_name(db, name_b)
        if not node_a:
            raise ValueError(f"未找到知识节点: {name_a}")
        if not node_b:
            raise ValueError(f"未找到知识节点: {name_b}")
        result = await analyze_pair(db, node_a["id"], node_b["id"])
        result["node_a_name"] = node_a["name"]
        result["node_b_name"] = node_b["name"]
        return {
            "type": "pair_analysis",
            "data": result,
        }

    elif skill == "derive_knowledge":
        node_names = params.get("node_names", [])
        node_ids = []
        resolved_names = []
        for name in node_names:
            node = await _find_node_by_name(db, name)
            if node:
                node_ids.append(node["id"])
                resolved_names.append(node["name"])
        if not node_ids:
            raise ValueError(f"未找到任何匹配的知识节点: {node_names}")
        result = await derive_knowledge(db, node_ids)
        result["resolved_names"] = resolved_names
        return {
            "type": "derive_result",
            "data": result,
        }

    elif skill == "get_domain_digest":
        domain = params.get("domain", "")
        if not domain:
            raise ValueError("请指定领域名称")
        domain_obj = await generate_domain_digest(db, domain)
        await db.commit()
        return {
            "type": "domain_digest",
            "data": {
                "name": domain_obj.name,
                "digest_markdown": domain_obj.digest_markdown,
                "digest_version": domain_obj.digest_version,
                "digest_node_count": domain_obj.digest_node_count,
                "digest_paper_count": domain_obj.digest_paper_count,
                "digest_relation_count": domain_obj.digest_relation_count,
            },
        }

    elif skill == "cross_domain_analysis":
        domain_a = params.get("domain_a", "")
        domain_b = params.get("domain_b", "")
        if not domain_a or not domain_b:
            raise ValueError("请指定两个领域")
        result = await cross_domain_analysis(db, domain_a, domain_b)
        await db.commit()
        return {
            "type": "cross_domain_analysis",
            "data": result,
        }

    elif skill == "list_domains":
        domains = await list_all_domains_with_digest(db)
        items = []
        for d in domains:
            items.append(
                {
                    "name": d.name,
                    "label": DOMAIN_LABELS.get(d.name, d.name),
                    "has_digest": bool(d.digest_markdown),
                    "digest_version": d.digest_version or 0,
                    "node_count": d.digest_node_count or 0,
                    "paper_count": d.digest_paper_count or 0,
                    "is_stale": d.digest_is_stale,
                }
            )
        return {
            "type": "domain_list",
            "data": {"domains": items, "total": len(items)},
        }

    return None


async def _generate_summary(
    skill: str,
    params: dict,
    result: dict | None,
    reply_prefix: str,
    messages: list[dict],
) -> str:
    """根据技能执行结果生成自然语言回复"""

    if skill == "general_chat":
        # 通用对话直接让 LLM 回答
        chat_msgs = [
            {
                "role": "system",
                "content": (
                    "你是 Knowledge Nexus 的 AI 助手，一个跨领域知识关联引擎。"
                    "你可以帮助用户发现知识关联、分析领域、搜索知识库。"
                    "回答简洁友好，使用 Markdown 格式。"
                ),
            },
            *[{"role": m["role"], "content": m["content"]} for m in messages[-6:]],
        ]
        return await chat_completion(messages=chat_msgs, temperature=0.7, max_tokens=800)

    if result is None:
        return f"{reply_prefix}\n\n未获得有效结果。"

    data_type = result.get("type", "")
    data = result.get("data", {})

    # 根据不同类型生成摘要文本
    if data_type == "search_results":
        items = data.get("items", [])
        if not items:
            return f"{reply_prefix}\n\n未找到与「{params.get('query', '')}」相关的知识。"
        summary_lines = [f"{reply_prefix}\n\n找到 **{len(items)}** 条相关结果：\n"]
        for item in items[:8]:
            icon = "📄" if item.get("type") == "paper" else "💡"
            summary_lines.append(f"- {icon} **{item['name']}** — {item.get('summary', '')[:80]}")
        return "\n".join(summary_lines)

    elif data_type == "discoveries":
        discoveries = data.get("discoveries", [])
        if not discoveries:
            return f"{reply_prefix}\n\n知识网络已经很完善，AI 未发现新的关联。"
        summary_lines = [f"{reply_prefix}\n\n发现了 **{len(discoveries)}** 条跨域关联：\n"]
        for d in discoveries:
            summary_lines.append(
                f"- **{d['source_name']}** → **{d['target_name']}** "
                f"[{d['relation_type']}] (置信度 {d['confidence']:.0%})\n"
                f"  {d['description'][:100]}"
            )
        return "\n".join(summary_lines)

    elif data_type == "pair_analysis":
        status = "✅ 存在关联" if data.get("has_relation") else "❌ 无明显关联"
        return (
            f"{reply_prefix}\n\n"
            f"### {data.get('node_a_name', '')} ↔ {data.get('node_b_name', '')} 分析结果\n\n"
            f"**状态**: {status} | **类型**: {data.get('relation_type', '')} | "
            f"**置信度**: {data.get('confidence', 0):.0%}\n\n"
            f"**描述**: {data.get('description', '')}\n\n"
            f"- 🏗️ **结构类比**: {data.get('structural_analogy', '')}\n"
            f"- 🔗 **因果联系**: {data.get('causal_link', '')}\n"
            f"- 🤝 **互补性**: {data.get('complementarity', '')}\n"
            f"- 🎯 **统一框架**: {data.get('unified_framework', '')}\n\n"
            f"> 💡 **新启示**: {data.get('new_insight', '')}"
        )

    elif data_type == "derive_result":
        lines = [f"{reply_prefix}\n"]
        pattern = data.get("abstract_pattern")
        if pattern:
            lines.append(f"### 🔮 深层模式: {pattern['name']}\n{pattern['description']}\n")
        transfers = data.get("transfer_ideas", [])
        if transfers:
            lines.append("### 🔄 知识迁移方向\n")
            for t in transfers:
                lines.append(
                    f"- **{t['from_domain']}** → **{t['to_domain']}**: {t['idea']} [{t['feasibility']}]"
                )
        hypotheses = data.get("new_hypotheses", [])
        if hypotheses:
            lines.append("\n### 🔬 新研究假设\n")
            for h in hypotheses:
                lines.append(f"- {h['hypothesis']} (影响: {h['impact']})")
        return "\n".join(lines)

    elif data_type == "domain_digest":
        name = data.get("name", "")
        label = DOMAIN_LABELS.get(name, name)
        return (
            f"{reply_prefix}\n\n"
            f"### {label} 领域摘要 (v{data.get('digest_version', 1)})\n"
            f"📊 {data.get('digest_node_count', 0)} 节点 | "
            f"{data.get('digest_paper_count', 0)} 论文 | "
            f"{data.get('digest_relation_count', 0)} 关联\n\n"
            f"{data.get('digest_markdown', '暂无摘要')}"
        )

    elif data_type == "cross_domain_analysis":
        domain_a_label = DOMAIN_LABELS.get(data.get("domain_a", ""), data.get("domain_a", ""))
        domain_b_label = DOMAIN_LABELS.get(data.get("domain_b", ""), data.get("domain_b", ""))
        summary = data.get("summary", "")
        lines = [
            f"{reply_prefix}\n\n"
            f"### 🔗 {domain_a_label} ↔ {domain_b_label} 跨域分析\n\n"
            f"> {summary}\n"
        ]
        analogies = data.get("analogies", [])
        if analogies:
            lines.append("\n**🪞 结构类比**:\n")
            for a in analogies:
                lines.append(
                    f"- **{a['concept_a']}** ≈ **{a['concept_b']}** [{a['depth']}]: {a['description']}"
                )
        transfers = data.get("transfer_ideas", [])
        if transfers:
            lines.append("\n**🔄 知识迁移**:\n")
            for t in transfers:
                lines.append(
                    f"- {t['from_domain']} → {t['to_domain']}: {t['idea']} [{t['feasibility']}]"
                )
        return "\n".join(lines)

    elif data_type == "domain_list":
        domains = data.get("domains", [])
        lines = [f"{reply_prefix}\n\n当前知识库共有 **{len(domains)}** 个领域：\n"]
        for d in domains:
            status = "✅" if d["has_digest"] else "⬜"
            lines.append(
                f"- {status} {d['label']} — "
                f"{d['node_count']} 节点, {d['paper_count']} 论文"
                f"{' (摘要已过期)' if d['is_stale'] else ''}"
            )
        lines.append("\n💡 你可以说「生成XX领域摘要」或「分析XX和YY的跨域关联」来深入了解。")
        return "\n".join(lines)

    return f"{reply_prefix}\n\n操作完成。"
