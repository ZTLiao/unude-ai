from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(64), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    credits: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    task_type: Mapped[str] = mapped_column(String(16))  # image | video | chat
    prompt: Mapped[str] = mapped_column(Text)
    ratio: Mapped[str] = mapped_column(String(16), default="1:1")
    model: Mapped[str] = mapped_column(String(64))
    provider: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending|running|succeeded|failed
    progress: Mapped[int] = mapped_column(Integer, default=0)
    cost_credits: Mapped[int] = mapped_column(Integer, default=0)
    result_url: Mapped[str] = mapped_column(String(512), default="")
    error: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Work(Base):
    __tablename__ = "works"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    task_id: Mapped[int] = mapped_column(Integer, index=True)
    work_type: Mapped[str] = mapped_column(String(16))  # image | video
    title: Mapped[str] = mapped_column(String(128), default="")
    prompt: Mapped[str] = mapped_column(Text)
    media_url: Mapped[str] = mapped_column(String(512))
    model: Mapped[str] = mapped_column(String(64))
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    is_public: Mapped[int] = mapped_column(Integer, default=1)  # 1 公开进社区广场
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
