"""模型目录 + Provider 路由注册表。

- model key 全局唯一,前端 Create 页的选择列表来自 MODEL_CATALOG
- cost_credits 为每次生成的积分消耗
- SiliconFlow 可用(有 Key)时优先,否则降级到免费 Provider
"""
from app.core.config import settings
from app.providers.base import BaseProvider
from app.providers.mock import MockProvider
from app.providers.pollinations import PollinationsProvider
from app.providers.siliconflow import SiliconFlowProvider

_providers: dict[str, BaseProvider] = {
    "mock": MockProvider(),
    "pollinations": PollinationsProvider(),
    "siliconflow": SiliconFlowProvider(),
}


def siliconflow_enabled() -> bool:
    return bool(settings.siliconflow_api_key)


# 模型目录: type=image|video|chat
MODEL_CATALOG: list[dict] = [
    {
        "key": "flux-schnell",
        "name": "Flux.1 Schnell",
        "type": "image",
        "desc": "高质量文生图,出图快",
        "cost_credits": 5,
        "provider": "siliconflow" if siliconflow_enabled() else "pollinations",
    },
    {
        "key": "kolors-free",
        "name": "Kolors 免费",
        "type": "image",
        "desc": "免费文生图,中文友好",
        "cost_credits": 0,
        "provider": "pollinations",
    },
    {
        "key": "wan-t2v",
        "name": "Wan2.2 文生视频",
        "type": "video",
        "desc": "AI 文生视频(需要 SiliconFlow)",
        "cost_credits": 30,
        "provider": "siliconflow",
    },
    {
        "key": "mock-video",
        "name": "视频演示(Mock)",
        "type": "video",
        "desc": "链路演示占位视频,不消耗外部额度",
        "cost_credits": 2,
        "provider": "mock",
    },
    {
        "key": "chat-free",
        "name": "智能助手",
        "type": "chat",
        "desc": "对话模型(Pollinations 免费 / Qwen)",
        "cost_credits": 1,
        "provider": "pollinations" if not siliconflow_enabled() else "siliconflow",
    },
]

MODEL_MAP = {m["key"]: m for m in MODEL_CATALOG}


def get_provider(name: str) -> BaseProvider:
    return _providers[name]


def resolve_provider(model_key: str) -> tuple[BaseProvider, dict]:
    """根据模型 key 取 Provider;目标 Provider 不可用时自动降级。"""
    model = MODEL_MAP[model_key]
    provider = _providers[model["provider"]]
    # SiliconFlow 未配置 Key 时降级
    if provider.name == "siliconflow" and not siliconflow_enabled():
        if model["type"] == "image":
            provider = _providers["pollinations"]
        elif model["type"] == "video":
            provider = _providers["mock"]
        elif model["type"] == "chat":
            provider = _providers["pollinations"]
    return provider, model
