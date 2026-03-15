import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


# 多对多关联表：论文 <-> 作者
paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("paper_id", String, ForeignKey("papers.id"), primary_key=True),
    Column("author_id", String, ForeignKey("authors.id"), primary_key=True),
)

# 多对多关联表：论文 <-> 标签
paper_tags = Table(
    "paper_tags",
    Base.metadata,
    Column("paper_id", String, ForeignKey("papers.id"), primary_key=True),
    Column("tag", String, primary_key=True),
)


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=gen_id)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    abstract: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(Integer)
    venue: Mapped[str | None] = mapped_column(String(200))
    domain_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("domains.id"))
    pdf_path: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(500))
    doi: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    arxiv_id: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    s2_id: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    influential_citation_count: Mapped[int] = mapped_column(Integer, default=0)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    key_contributions: Mapped[str | None] = mapped_column(Text)  # 短名称
    summary: Mapped[str | None] = mapped_column(String(500))  # 一句话简介
    fields_of_study: Mapped[str | None] = mapped_column(String(500))  # 所属领域（逗号分隔）
    ai_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    domain: Mapped["Domain | None"] = relationship(back_populates="papers")
    authors: Mapped[list["Author"]] = relationship(
        secondary=paper_authors, back_populates="papers"
    )

    def __repr__(self):
        return f"<Paper {self.id}: {self.title[:50]}>"


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    affiliation: Mapped[str | None] = mapped_column(String(300))
    s2_id: Mapped[str | None] = mapped_column(String(50), unique=True)

    papers: Mapped[list["Paper"]] = relationship(
        secondary=paper_authors, back_populates="authors"
    )


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("domains.id"))

    papers: Mapped[list["Paper"]] = relationship(back_populates="domain")
    children: Mapped[list["Domain"]] = relationship(back_populates="parent")
    parent: Mapped["Domain | None"] = relationship(
        back_populates="children", remote_side=[id]
    )


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    domain_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("domains.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Relation(Base):
    """论文/概念间的关联（同时存入 Neo4j 图谱）"""
    __tablename__ = "relations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=gen_id)
    source_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)  # paper / concept
    target_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CITES, IMPROVES, ANALOGOUS_TO...
    description: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    ai_generated: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(20), default="confirmed")  # confirmed / pending / rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CrawlTask(Base):
    """爬取任务记录"""
    __tablename__ = "crawl_tasks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=gen_id)
    domain: Mapped[str] = mapped_column(String(100))
    subdomain: Mapped[str | None] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(50), default="openalex")
    year_from: Mapped[int] = mapped_column(Integer)
    year_to: Mapped[int] = mapped_column(Integer)
    min_citations: Mapped[int] = mapped_column(Integer, default=100)
    max_papers: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    searched: Mapped[int] = mapped_column(Integer, default=0)
    candidates: Mapped[int] = mapped_column(Integer, default=0)
    imported: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
