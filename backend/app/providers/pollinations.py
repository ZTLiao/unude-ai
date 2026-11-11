"""Pollinations.ai 免费模型(无需 API Key):文生图 + 对话。"""
import re

import httpx

from app.core.config import settings
from app.providers.base import BaseProvider, GenerationResult

SIZE_RE = re.compile(r"(\d+)x(\d+)")


class PollinationsProvider(BaseProvider):
    name = "pollinations"

    def text_to_image(self, prompt: str, size: str = "1024x1024") -> GenerationResult:
        m = SIZE_RE.match(size)
        w, h = (m.group(1), m.group(2)) if m else ("1024", "1024")
        url = f"{settings.pollinations_image_url}/{prompt}?width={w}&height={h}&nologo=true&referrer=unudeai.com"
        resp = httpx.get(url, timeout=120, follow_redirects=True)
        resp.raise_for_status()
        if "image" not in resp.headers.get("content-type", ""):
            raise RuntimeError(f"Pollinations 返回非图片: {resp.headers.get('content-type')}")
        return GenerationResult(data=resp.content, ext="jpg")

    def chat(self, messages: list[dict], model: str = "") -> str:
        # 端点降级链: POST /openai -> POST / -> GET /{prompt}
        # referrer 参数用于 Pollinations 免费额度识别
        body = {"model": model or "openai", "messages": messages, "referrer": "unudeai.com"}
        for url in (
            settings.pollinations_text_url,
            settings.pollinations_text_url.removesuffix("/openai"),
        ):
            try:
                resp = httpx.post(url, json=body, timeout=120)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except (httpx.HTTPError, KeyError, ValueError):
                continue
        # 兜底: GET 端点,只取最后一轮用户消息并截断(免费额度限制)
        user_text = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
        )
        resp = httpx.get(
            f"{settings.pollinations_text_url.removesuffix('/openai')}/{user_text[:300]}", params={"referrer": "unudeai.com"},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.text
