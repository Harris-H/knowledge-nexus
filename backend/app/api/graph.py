from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import Paper, Relation
from app.schemas.schemas import SubgraphResponse, GraphNode, GraphEdge, RelationCreate

router = APIRouter()


@router.get("/full", response_model=SubgraphResponse)
async def get_full_graph(
    min_citations: int = Query(0, ge=0, description="最低引用量过滤"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """获取完整知识图谱（可按引用量过滤）"""
    # 获取所有符合条件的论文
    query = select(Paper).where(Paper.citation_count >= min_citations).order_by(
        Paper.citation_count.desc()
    ).limit(limit)
    result = await db.execute(query)
    papers = result.scalars().all()

    paper_ids = {p.id for p in papers}
    nodes = []
    for p in papers:
        nodes.append(GraphNode(
            id=p.id,
            type="paper",
            label=p.key_contributions or p.title,  # 优先使用短名称
            properties={
                "year": p.year,
                "citations": p.citation_count,
                "impact_score": p.impact_score,
                "venue": p.venue or "",
                "full_title": p.title,
            },
        ))

    # 获取这些论文之间的所有关系
    edges = []
    if paper_ids:
        result = await db.execute(
            select(Relation).where(
                Relation.source_id.in_(paper_ids),
                Relation.target_id.in_(paper_ids),
                Relation.status == "confirmed",
            )
        )
        for rel in result.scalars().all():
            edges.append(GraphEdge(
                id=rel.id,
                source=rel.source_id,
                target=rel.target_id,
                type=rel.relation_type,
                properties={
                    "description": rel.description or "",
                    "confidence": rel.confidence,
                },
            ))

    return SubgraphResponse(nodes=nodes, edges=edges)


@router.get("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(
    center: str = Query(..., description="中心节点 ID"),
    depth: int = Query(1, ge=1, le=3, description="展开深度"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """获取以指定节点为中心的子图"""
    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    # 从关系表获取相关边
    visited = set()
    current_ids = {center}

    for _ in range(depth):
        if not current_ids:
            break

        next_ids = set()
        for node_id in current_ids:
            if node_id in visited:
                continue
            visited.add(node_id)

            # 查找以该节点为 source 或 target 的关系
            result = await db.execute(
                select(Relation).where(
                    (Relation.source_id == node_id) | (Relation.target_id == node_id),
                    Relation.status == "confirmed",
                )
            )
            relations = result.scalars().all()

            for rel in relations:
                edges.append(GraphEdge(
                    id=rel.id,
                    source=rel.source_id,
                    target=rel.target_id,
                    type=rel.relation_type,
                    properties={
                        "description": rel.description or "",
                        "confidence": rel.confidence,
                        "ai_generated": rel.ai_generated,
                    },
                ))
                next_ids.add(rel.source_id)
                next_ids.add(rel.target_id)

        current_ids = next_ids - visited

    # 填充节点信息
    all_node_ids = visited | current_ids
    for nid in all_node_ids:
        result = await db.execute(select(Paper).where(Paper.id == nid))
        paper = result.scalar_one_or_none()
        if paper:
            nodes[nid] = GraphNode(
                id=paper.id,
                type="paper",
                label=paper.key_contributions or paper.title,
                properties={
                    "year": paper.year,
                    "citations": paper.citation_count,
                    "full_title": paper.title,
                },
            )

    # 限制返回数量
    node_list = list(nodes.values())[:limit]
    edge_list = edges[:limit * 2]

    return SubgraphResponse(nodes=node_list, edges=edge_list)


@router.post("/relations", status_code=201)
async def create_relation(data: RelationCreate, db: AsyncSession = Depends(get_db)):
    """手动创建关联"""
    from app.models.models import gen_id

    relation = Relation(
        id=gen_id(),
        source_id=data.source_id,
        source_type="paper",
        target_id=data.target_id,
        target_type="paper",
        relation_type=data.relation_type,
        description=data.description,
        confidence=data.confidence,
        ai_generated=False,
        status="confirmed",
    )
    db.add(relation)
    await db.flush()

    return {"id": relation.id, "status": "created"}
