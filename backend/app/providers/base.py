"""Provider 抽象基类:文生图 / 文生视频 / 对话。"""
from abc import ABC, abstractmethod


class GenerationResult:
    def __init__(self, data: bytes | None = None, url: str = "", ext: str = "png"):
        self.data = data  # 二进制内容(由调用方落盘)
        self.url = url  # 或外部 URL
        self.ext = ext


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def text_to_image(self, prompt: str, size: str = "1024x1024") -> GenerationResult:
        ...

    def text_to_video(self, prompt: str, duration: int = 5) -> GenerationResult:
        raise NotImplementedError(f"{self.name} 不支持文生视频")

    def chat(self, messages: list[dict], model: str = "") -> str:
        raise NotImplementedError(f"{self.name} 不支持对话")
