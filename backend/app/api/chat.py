from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.auth import get_current_user
from app.models.entities import User
from app.providers.registry import MODEL_MAP, resolve_provider

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@router.post("")
def chat(req: ChatRequest, user: User = Depends(get_current_user)):
    model = MODEL_MAP.get("chat-free")
    if not req.message.strip():
        raise HTTPException(400, "消息不能为空")
    provider, _ = resolve_provider("chat-free")
    messages = [{"role": "system", "content": "你是 UnudeAI 平台的 AI 创作助手,亲切简洁地回答。"}]
    messages += req.history[-10:]
    messages.append({"role": "user", "content": req.message})
    try:
        reply = provider.chat(messages, model=model["key"])
    except NotImplementedError:
        raise HTTPException(400, "当前 Provider 不支持对话")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"对话服务暂不可用: {exc}")
    return {"reply": reply}
