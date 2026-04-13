"""
AI 分析 API — 利用 LLM 发现跨领域知识关联和推导新知识。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import KnowledgeNode, Paper
from app.services.ai.analyzer import (
    discover_relations,
    derive_knowledge,
    analyze_pair,
    save_discovered_relations,
)
from app.services.ai.chat_service import process_chat

router = APIRouter()


class DiscoverRequest(BaseModel):
    limit: int = 8
    domains: list[str] | None = None  # 限定领域，None=全部


class DeriveRequest(BaseModel):
    node_ids: list[str]  # 要分析的知识节点 ID 列表


class AnalyzePairRequest(BaseModel):
    node_a_id: str
    node_b_id: str


class SaveDiscoveriesRequest(BaseModel):
    discoveries: list[dict]
    auto_confirm: bool = False


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@router.post("/discover")
async def api_discover_relations(
    req: DiscoverRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    🔍 AI 自动发现知识库中的跨领域关联。
    扫描所有知识节点和论文，找出尚未建立但可能存在的深层联系。
    """
    try:
        result = await discover_relations(db, limit=req.limit, domains=req.domains)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析失败: {str(e)}")


@router.post("/derive")
async def api_derive_knowledge(
    req: DeriveRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    🧠 基于一组知识节点推导新知识。
    分析共同模式、迁移可能、缺失环节、新假设。
    """
    if not req.node_ids:
        raise HTTPException(status_code=400, detail="请提供至少一个知识节点 ID")
    try:
        result = await derive_knowledge(db, req.node_ids)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 推导失败: {str(e)}")


@router.post("/analyze-pair")
async def api_analyze_pair(
    req: AnalyzePairRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    🔬 深度分析两个知识节点之间的潜在关联。
    从结构类比、因果联系、互补性、统一框架等维度分析。
    """
    try:
        result = await analyze_pair(db, req.node_a_id, req.node_b_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析失败: {str(e)}")


@router.post("/save-discoveries")
async def api_save_discoveries(
    req: SaveDiscoveriesRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    💾 保存 AI 发现的关联到数据库。
    默认保存为 pending 状态等待审核，设 auto_confirm=true 直接确认。
    """
    if not req.discoveries:
        return {"saved": 0}
    try:
        saved = await save_discovered_relations(
            db, req.discoveries, auto_confirm=req.auto_confirm
        )
        return {"saved": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.get("/nodes")
async def api_list_all_nodes(
    domain: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """列出所有知识节点和论文（用于前端选择器）"""
    items = []
    # 知识节点
    kn_q = select(KnowledgeNode)
    if domain:
        kn_q = kn_q.where(KnowledgeNode.domain == domain)
    kn_result = await db.execute(kn_q)
    for kn in kn_result.scalars().all():
        items.append(
            {
                "id": kn.id,
                "name": kn.name,
                "type": "knowledge_node",
                "node_type": kn.node_type,
                "domain": kn.domain,
                "summary": kn.summary or "",
            }
        )
    # 论文
    from app.api.graph import _normalize_paper_domain

    p_result = await db.execute(select(Paper))
    for p in p_result.scalars().all():
        p_domain = _normalize_paper_domain(p.fields_of_study)
        if domain and p_domain != domain:
            continue
        items.append(
            {
                "id": p.id,
                "name": p.key_contributions or p.title,
                "type": "paper",
                "node_type": "paper",
                "domain": p_domain,
                "summary": p.summary or "",
            }
        )
    # 领域统计
    domain_counts = {}
    for item in items:
        d = item["domain"]
        domain_counts[d] = domain_counts.get(d, 0) + 1
    return {"items": items, "total": len(items), "domain_counts": domain_counts}


@router.post("/chat")
async def api_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    🤖 对话式 AI 助手。
    接收消息历史，自动识别意图并调用对应技能，返回结构化结果。
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="请提供至少一条消息")
    try:
        result = await process_chat(
            db,
            [{"role": m.role, "content": m.content} for m in req.messages],
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")
