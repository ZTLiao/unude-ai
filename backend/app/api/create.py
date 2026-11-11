from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.entities import GenerationTask, User
from app.providers.registry import MODEL_CATALOG, MODEL_MAP, resolve_provider
from app.services.generation import run_generation_task

from concurrent.futures import ThreadPoolExecutor

router = APIRouter(tags=["create"])
executor = ThreadPoolExecutor(max_workers=4)


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    ratio: str = "1:1"


@router.get("/models")
def list_models():
    return MODEL_CATALOG


@router.post("/generate")
def generate(
    req: GenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.model not in MODEL_MAP:
        raise HTTPException(400, "未知模型")
    if not req.prompt.strip():
        raise HTTPException(400, "提示词不能为空")

    _, model = resolve_provider(req.model)
    cost = model["cost_credits"]
    if user.credits < cost:
        raise HTTPException(400, f"积分不足,本次需要 {cost} 积分")

    user.credits -= cost
    task = GenerationTask(
        user_id=user.id,
        task_type=model["type"],
        prompt=req.prompt.strip(),
        ratio=req.ratio,
        model=req.model,
        provider=model["provider"],
        cost_credits=cost,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    executor.submit(run_generation_task, task.id)
    return {"task_id": task.id, "cost_credits": cost, "credits": user.credits}


@router.get("/tasks/{task_id}")
def task_status(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.get(GenerationTask, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(404, "任务不存在")
    return {
        "id": task.id,
        "status": task.status,
        "progress": task.progress,
        "result_url": task.result_url,
        "error": task.error,
        "model": task.model,
        "prompt": task.prompt,
    }
