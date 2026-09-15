from fastapi import APIRouter
from models.schemas import ContextRequest, ContextResponse, HistoryResponse
from services.context_service import context_service
from services.task_service import task_service

router = APIRouter(prefix="/api/brain", tags=["Context & History"])


@router.post("/context", response_model=ContextResponse, summary="Save and manage conversation context")
async def save_context(payload: ContextRequest):
    """
    Save conversation context manually or inspect recent commands and the active last plan.
    """
    if payload.input:
        context_service.add_command(
            text=payload.input,
            metadata=payload.metadata,
        )

    recent = context_service.get_recent_commands(limit=10)
    last_plan = context_service.get_last_plan()

    return {
        "status": "success",
        "recent_commands": recent,
        "last_plan": last_plan,
    }


@router.get("/context", response_model=ContextResponse, summary="Get active conversation context")
async def get_context():
    """
    Retrieve the last 10 commands and last plan from conversation context.
    """
    recent = context_service.get_recent_commands(limit=10)
    last_plan = context_service.get_last_plan()
    return {
        "status": "success",
        "recent_commands": recent,
        "last_plan": last_plan,
    }


@router.get("/history", response_model=HistoryResponse, summary="Retrieve last 20 planned tasks")
async def get_task_history():
    """
    Return the last 20 planned tasks.
    """
    tasks = task_service.get_history(limit=20)
    return {
        "total": len(tasks),
        "tasks": tasks,
    }
