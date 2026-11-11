"""SiliconFlow 硅基流动适配器(注册送额度,含 Flux 生图/Qwen 对话/视频模型)。

填入 SILICONFLOW_API_KEY 后启用。
"""
import base64

import httpx

from app.core.config import settings
from app.providers.base import BaseProvider, GenerationResult


class SiliconFlowProvider(BaseProvider):
    name = "siliconflow"

    def _headers(self) -> dict:
        if not settings.siliconflow_api_key:
            raise RuntimeError("未配置 SILICONFLOW_API_KEY,请填写 .env 后重启")
        return {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
            "Content-Type": "application/json",
        }

    def text_to_image(self, prompt: str, size: str = "1024x1024") -> GenerationResult:
        body = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": prompt,
            "image_size": size,
        }
        resp = httpx.post(
            f"{settings.siliconflow_base_url}/images/generations",
            headers=self._headers(),
            json=body,
            timeout=120,
        )
        resp.raise_for_status()
        url = resp.json()["images"][0]["url"]
        return GenerationResult(url=url, ext="png")

    def chat(self, messages: list[dict], model: str = "") -> str:
        resp = httpx.post(
            f"{settings.siliconflow_base_url}/chat/completions",
            headers=self._headers(),
            json={
                "model": model or "Qwen/Qwen2.5-72B-Instruct",
                "messages": messages,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def text_to_video(self, prompt: str, duration: int = 5) -> GenerationResult:
        """视频为异步接口:提交 -> 轮询取结果(同步封装)。"""
        headers = self._headers()
        body = {"model": "Wan-AI/Wan2.2-T2V-A14B", "prompt": prompt}
        resp = httpx.post(
            f"{settings.siliconflow_base_url}/video/submit",
            headers=headers,
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        request_id = resp.json()["requestId"]
        import time

        for _ in range(60):  # 最多等 5 分钟
            time.sleep(5)
            poll = httpx.get(
                f"{settings.siliconflow_base_url}/video/status",
                params={"requestId": request_id},
                headers=headers,
                timeout=30,
            )
            poll.raise_for_status()
            data = poll.json()
            if data.get("status") == "Succeed":
                url = data["results"]["videos"][0]["url"]
                dl = httpx.get(url, timeout=300, follow_redirects=True)
                dl.raise_for_status()
                return GenerationResult(data=dl.content, ext="mp4")
            if data.get("status") == "Failed":
                raise RuntimeError(f"视频生成失败: {data}")
        raise TimeoutError("视频生成超时")
