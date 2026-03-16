from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import KnowledgeNode, Relation, gen_id
from app.schemas.schemas import (
    KnowledgeNodeCreate, KnowledgeNodeResponse, KnowledgeNodeList,
)

router = APIRouter()


@router.get("/", response_model=KnowledgeNodeList)
async def list_knowledge_nodes(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    domain: str | None = Query(None),
    node_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """列出知识节点，支持按领域和类型过滤"""
    query = select(KnowledgeNode)
    count_query = select(func.count(KnowledgeNode.id))

    if domain:
        query = query.where(KnowledgeNode.domain == domain)
        count_query = count_query.where(KnowledgeNode.domain == domain)
    if node_type:
        query = query.where(KnowledgeNode.node_type == node_type)
        count_query = count_query.where(KnowledgeNode.node_type == node_type)

    total = (await db.execute(count_query)).scalar() or 0
    rows = (
        await db.execute(
            query.order_by(KnowledgeNode.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    ).scalars().all()

    return KnowledgeNodeList(
        items=[KnowledgeNodeResponse.model_validate(r) for r in rows],
        total=total,
    )


@router.post("/", response_model=KnowledgeNodeResponse, status_code=201)
async def create_knowledge_node(
    data: KnowledgeNodeCreate, db: AsyncSession = Depends(get_db),
):
    """创建知识节点"""
    node = KnowledgeNode(id=gen_id(), **data.model_dump())
    db.add(node)
    await db.flush()
    # 标记对应领域摘要为过期
    from app.services.digest_service import mark_domain_digest_stale
    await mark_domain_digest_stale(db, node.domain)
    return KnowledgeNodeResponse.model_validate(node)


@router.delete("/{node_id}")
async def delete_knowledge_node(node_id: str, db: AsyncSession = Depends(get_db)):
    """删除知识节点及其关联关系"""
    result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        return {"error": "not found"}

    domain_name = node.domain
    # 删除关联的关系
    await db.execute(
        delete(Relation).where(
            (Relation.source_id == node_id) | (Relation.target_id == node_id)
        )
    )
    await db.delete(node)
    await db.flush()
    # 标记对应领域摘要为过期
    from app.services.digest_service import mark_domain_digest_stale
    await mark_domain_digest_stale(db, domain_name)
    return {"status": "deleted", "id": node_id}


class BatchDeleteRequest(BaseModel):
    ids: list[str]


@router.post("/batch-delete")
async def batch_delete_knowledge_nodes(
    req: BatchDeleteRequest, db: AsyncSession = Depends(get_db),
):
    """批量删除知识节点"""
    if not req.ids:
        return {"deleted": 0}

    # 先收集受影响的领域
    result = await db.execute(
        select(KnowledgeNode.domain).where(KnowledgeNode.id.in_(req.ids)).distinct()
    )
    affected_domains = [row[0] for row in result]

    # 删除关联关系
    await db.execute(
        delete(Relation).where(
            Relation.source_id.in_(req.ids) | Relation.target_id.in_(req.ids)
        )
    )
    # 删除节点
    await db.execute(
        delete(KnowledgeNode).where(KnowledgeNode.id.in_(req.ids))
    )
    await db.flush()

    # 标记受影响领域摘要为过期
    from app.services.digest_service import mark_domain_digest_stale
    for domain_name in affected_domains:
        await mark_domain_digest_stale(db, domain_name)

    return {"deleted": len(req.ids)}
