from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "Knowledge Nexus"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库 - 开发阶段默认使用 SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./knowledge_nexus.db"

    # Neo4j 图数据库（可选，不配置则跳过图谱功能）
    NEO4J_URI: str = ""
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # Qdrant 向量数据库（可选）
    QDRANT_HOST: str = ""
    QDRANT_PORT: int = 6333

    # Meilisearch（可选）
    MEILISEARCH_HOST: str = ""
    MEILISEARCH_KEY: str = ""

    # Redis（可选）
    REDIS_URL: str = ""

    # AI / LLM（兼容 OpenAI 格式，支持 Doubao/DeepSeek/OpenAI/Ollama）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"  # 默认豆包
    LLM_MODEL: str = "doubao-seed-2-0-lite-260215"
    # DeepSeek: LLM_BASE_URL=https://api.deepseek.com/v1  LLM_MODEL=deepseek-chat
    # OpenAI:   LLM_BASE_URL=https://api.openai.com/v1    LLM_MODEL=gpt-4o-mini
    # Ollama:   LLM_BASE_URL=http://localhost:11434/v1     LLM_MODEL=qwen2.5

    # 保留旧字段兼容
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""

    # Semantic Scholar API
    SEMANTIC_SCHOLAR_API_KEY: str = ""

    # OpenAlex（免费学术 API）
    OPENALEX_EMAIL: str = ""  # 可选，提供后进入 polite pool 获得更快响应

    # 文件存储
    STORAGE_PATH: Path = Path("./storage")

    # 爬虫配置
    CRAWLER_SOURCE: str = "openalex"  # 数据源：openalex（默认，快速免费）或 semantic_scholar
    CRAWLER_RATE_LIMIT: float = 3.5  # S2 请求间隔（秒），无 API key 建议 >=3
    CRAWLER_MAX_RETRIES: int = 3

    @property
    def papers_path(self) -> Path:
        path = self.STORAGE_PATH / "papers"
        path.mkdir(parents=True, exist_ok=True)
        return path

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
