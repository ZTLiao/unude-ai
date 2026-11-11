from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_user
from app.core.database import get_db
from app.models.entities import User, Work

router = APIRouter(tags=["works"])


@router.get("/works")
def list_works(
    only_mine: bool = False,
    work_type: str | None = None,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """社区广场(公开作品)或我的作品列表;未登录仅可浏览公开作品。"""
    if only_mine:
        if user is None:
            raise HTTPException(401, "未登录")
        q = db.query(Work).filter(Work.user_id == user.id)
    else:
        q = db.query(Work).filter(Work.is_public == 1)
    if work_type in ("image", "video"):
        q = q.filter(Work.work_type == work_type)
    works = q.order_by(desc(Work.created_at)).limit(50).all()
    return [_work_dto(w) for w in works]


@router.post("/works/{work_id}/like")
def like_work(work_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    work = db.get(Work, work_id)
    if not work:
        raise HTTPException(404, "作品不存在")
    work.like_count += 1
    db.commit()
    return {"like_count": work.like_count}


@router.get("/users/me/credits")
def my_credits(user: User = Depends(get_current_user)):
    return {"credits": user.credits}


def _work_dto(w: Work) -> dict:
    return {
        "id": w.id,
        "user_id": w.user_id,
        "work_type": w.work_type,
        "title": w.title,
        "prompt": w.prompt,
        "media_url": w.media_url,
        "model": w.model,
        "like_count": w.like_count,
        "created_at": str(w.created_at),
    }
