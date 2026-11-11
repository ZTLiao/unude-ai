"""生成任务执行器:后台线程执行,更新任务进度,产物落盘并登记作品。"""
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import GenerationTask, User, Work
from app.providers.registry import resolve_provider

_SIZE_MAP = {
    "1:1": "1024x1024",
    "3:4": "768x1024",
    "9:16": "768x1344",
    "16:9": "1344x768",
}


def _save_media(data: bytes, ext: str, subdir: str) -> str:
    media_root = Path(settings.media_dir) / subdir
    media_root.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{ext}"
    (media_root / filename).write_bytes(data)
    return f"/media/{subdir}/{filename}"


def run_generation_task(task_id: int):
    """在线程池中执行,自建 DB 会话(与请求会话隔离)。"""
    db: Session = SessionLocal()
    task = db.get(GenerationTask, task_id)
    if not task:
        return
    try:
        task.status = "running"
        task.progress = 10
        db.commit()

        provider, model = resolve_provider(task.model)
        size = _SIZE_MAP.get(task.ratio, "1024x1024")

        task.progress = 40
        db.commit()

        if task.task_type == "image":
            result = provider.text_to_image(task.prompt, size=size)
            subdir = "images"
        elif task.task_type == "video":
            result = provider.text_to_video(task.prompt)
            subdir = "videos"
        else:
            raise ValueError(f"不支持的任务类型: {task.task_type}")

        task.progress = 85
        db.commit()

        if result.data:
            url = _save_media(result.data, result.ext, subdir)
        else:
            url = result.url

        task.result_url = url
        task.status = "succeeded"
        task.progress = 100
        task.finished_at = datetime.now(timezone.utc)

        db.add(
            Work(
                user_id=task.user_id,
                task_id=task.id,
                work_type=task.task_type,
                title=task.prompt[:60],
                prompt=task.prompt,
                media_url=url,
                model=task.model,
            )
        )
        db.commit()
    except Exception as exc:  # noqa: BLE001 任务失败不中断服务
        task.status = "failed"
        task.error = str(exc)[:500]
        task.finished_at = datetime.now(timezone.utc)
        # 失败退还积分
        user = db.get(User, task.user_id)
        if user is not None:
            user.credits += task.cost_credits
        db.commit()
    finally:
        db.close()
