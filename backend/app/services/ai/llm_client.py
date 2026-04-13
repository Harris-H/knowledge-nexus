"""
LLM 客户端 — 兼容 OpenAI chat/completions 格式。
支持 Doubao / DeepSeek / OpenAI / Ollama 等 OpenAI 兼容 API。
"""

import json
import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def chat_completion(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> str:
    """
    调用 LLM chat/completions 接口，返回文本响应。
    """
    api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
    base_url = settings.LLM_BASE_URL or settings.OPENAI_BASE_URL
    model = settings.LLM_MODEL

    if not api_key:
        raise ValueError("未配置 LLM_API_KEY，请在 .env 文件中设置")
    if not base_url:
        raise ValueError("未配置 LLM_BASE_URL，请在 .env 文件中设置")

    url = f"{base_url.rstrip('/')}/chat/completions"

    body: dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        body["max_tokens"] = max_tokens

    logger.info(
        f"🤖 LLM 请求: model={model}, messages={len(messages)}, temp={temperature}"
    )

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=body,
        )
        resp.raise_for_status()

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    logger.info(f"✅ LLM 响应: {len(content)} 字符")
    return content


async def chat_completion_json(
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int | None = None,
) -> dict:
    """
    调用 LLM 并解析 JSON 响应（支持 markdown code block 包裹）。
    """
    content = await chat_completion(messages, temperature, max_tokens)

    # 提取 JSON（可能被 ```json ... ``` 包裹）
    import re

    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    json_str = json_match.group(1).strip() if json_match else content.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 解析失败: {e}\n原始内容: {content[:500]}")
        raise ValueError(f"LLM 返回的内容不是有效 JSON: {e}")
