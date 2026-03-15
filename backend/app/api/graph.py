from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import Paper, Relation, KnowledgeNode
from app.schemas.schemas import SubgraphResponse, GraphNode, GraphEdge, RelationCreate

router = APIRouter()


@router.get("/full", response_model=SubgraphResponse)
async def get_full_graph(
    min_citations: int = Query(0, ge=0, description="最低引用量过滤（仅论文）"),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """获取完整知识图谱（论文 + 知识节点）"""
    nodes = []
    all_node_ids = set()

    # 1. 获取论文节点
    query = select(Paper).where(Paper.citation_count >= min_citations).order_by(
        Paper.citation_count.desc()
    ).limit(limit)
    result = await db.execute(query)
    papers = result.scalars().all()

    for p in papers:
        all_node_ids.add(p.id)
        nodes.append(GraphNode(
            id=p.id,
            type="paper",
            label=p.key_contributions or p.title,
            properties={
                "year": p.year,
                "citations": p.citation_count,
                "impact_score": p.impact_score,
                "venue": p.venue or "",
                "full_title": p.title,
                "domain": (p.fields_of_study or "").split(",")[0].strip() if p.fields_of_study else "computer_science",
            },
        ))

    # 2. 获取所有知识节点
    kn_result = await db.execute(select(KnowledgeNode))
    kn_nodes = kn_result.scalars().all()

    for kn in kn_nodes:
        all_node_ids.add(kn.id)
        nodes.append(GraphNode(
            id=kn.id,
            type=kn.node_type,  # phenomenon / theorem / law / method / ...
            label=kn.name,
            properties={
                "year": kn.year,
                "domain": kn.domain,
                "summary": kn.summary or "",
                "source_info": kn.source_info or "",
                "node_type": kn.node_type,
                "description": kn.description or "",
            },
        ))

    # 3. 获取所有已确认的关系
    edges = []
    if all_node_ids:
        result = await db.execute(
            select(Relation).where(
                Relation.source_id.in_(all_node_ids),
                Relation.target_id.in_(all_node_ids),
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

    # 填充节点信息（论文 + 知识节点）
    all_node_ids = visited | current_ids
    for nid in all_node_ids:
        # 先查论文
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
                    "domain": (paper.fields_of_study or "").split(",")[0].strip() if paper.fields_of_study else "computer_science",
                },
            )
            continue
        # 再查知识节点
        result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.id == nid))
        kn = result.scalar_one_or_none()
        if kn:
            nodes[nid] = GraphNode(
                id=kn.id,
                type=kn.node_type,
                label=kn.name,
                properties={
                    "year": kn.year,
                    "domain": kn.domain,
                    "summary": kn.summary or "",
                    "node_type": kn.node_type,
                    "description": kn.description or "",
                },
            )

    # 限制返回数量
    node_list = list(nodes.values())[:limit]
    edge_list = edges[:limit * 2]

    return SubgraphResponse(nodes=node_list, edges=edge_list)


@router.post("/relations", status_code=201)
async def create_relation(data: RelationCreate, db: AsyncSession = Depends(get_db)):
    """手动创建关联（支持 paper↔paper, paper↔knowledge_node, knowledge_node↔knowledge_node）"""
    from app.models.models import gen_id

    # 自动推断 source_type 和 target_type
    async def infer_type(nid: str) -> str:
        r = await db.execute(select(Paper.id).where(Paper.id == nid))
        if r.scalar_one_or_none():
            return "paper"
        r = await db.execute(select(KnowledgeNode.id).where(KnowledgeNode.id == nid))
        if r.scalar_one_or_none():
            return "knowledge_node"
        return "unknown"

    source_type = await infer_type(data.source_id)
    target_type = await infer_type(data.target_id)

    relation = Relation(
        id=gen_id(),
        source_id=data.source_id,
        source_type=source_type,
        target_id=data.target_id,
        target_type=target_type,
        relation_type=data.relation_type,
        description=data.description,
        confidence=data.confidence,
        ai_generated=False,
        status="confirmed",
    )
    db.add(relation)
    await db.flush()

    return {"id": relation.id, "status": "created"}
