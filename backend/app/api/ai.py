"""
AI 分析 API — 利用 LLM 发现跨领域知识关联和推导新知识。
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ai.analyzer import (
    discover_relations,
    derive_knowledge,
    analyze_pair,
    save_discovered_relations,
)

router = APIRouter()


class DiscoverRequest(BaseModel):
    limit: int = 8  # 发现的最大关联数


class DeriveRequest(BaseModel):
    node_ids: list[str]  # 要分析的知识节点 ID 列表


class AnalyzePairRequest(BaseModel):
    node_a_id: str
    node_b_id: str


class SaveDiscoveriesRequest(BaseModel):
    discoveries: list[dict]
    auto_confirm: bool = False


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
        result = await discover_relations(db, limit=req.limit)
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
