from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.models.entities import User

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "未登录")
    user_id = decode_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "登录已过期")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """可选登录:未带 token 时返回 None(用于公开浏览接口)。"""
    if credentials is None:
        return None
    user_id = decode_token(credentials.credentials)
    if user_id is None:
        return None
    return db.get(User, user_id)


@router.post("/register")
def register(email: str, password: str, nickname: str = "", db: Session = Depends(get_db)):
    if not email or "@" not in email:
        raise HTTPException(400, "邮箱格式不正确")
    if len(password) < 4:
        raise HTTPException(400, "密码至少 4 位")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "该邮箱已注册")
    user = User(
        email=email,
        nickname=nickname or email.split("@")[0],
        hashed_password=hash_password(password),
        credits=settings.register_bonus_credits,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_access_token(user.id), "user": _user_dto(user)}


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(400, "邮箱或密码错误")
    return {"token": create_access_token(user.id), "user": _user_dto(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _user_dto(user)


def _user_dto(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "credits": user.credits,
    }
