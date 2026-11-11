"""Mock Provider:占位图/占位视频,保证无网环境下链路可跑通。"""
import struct
import zlib

from app.providers.base import BaseProvider, GenerationResult


def _png_solid(width: int, height: int, rgb: tuple) -> bytes:
    """生成纯色 PNG(标准库实现,无第三方依赖)。"""

    def chunk(tag: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(rgb) * width
    idat = zlib.compress(row * height)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )


class MockProvider(BaseProvider):
    name = "mock"

    def text_to_image(self, prompt: str, size: str = "1024x1024") -> GenerationResult:
        try:
            w, h = (int(x) for x in size.lower().split("x"))
        except ValueError:
            w, h = 1024, 1024
        # 用提示词长度映射一个颜色,便于肉眼区分任务
        rgb = ((len(prompt) * 37) % 256, (len(prompt) * 91) % 256, (len(prompt) * 53) % 256)
        return GenerationResult(data=_png_solid(w, h, rgb), ext="png")

    def text_to_video(self, prompt: str, duration: int = 5) -> GenerationResult:
        # Mock 视频返回一张大图并复用 .jpg 扩展名占位(真实 Provider 才返回 mp4)
        rgb = ((len(prompt) * 11) % 256, (len(prompt) * 7) % 256, 200)
        return GenerationResult(data=_png_solid(640, 360, rgb), ext="jpg")
