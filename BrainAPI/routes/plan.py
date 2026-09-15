import asyncio
import logging
from fastapi import APIRouter, HTTPException
from models.schemas import PlanRequest, PlanResponse
from services.intelligence_service import intelligent_plan
from services.context_service import context_service
from services.task_service import task_service

logger = logging.getLogger("routes.plan")

router = APIRouter(prefix="/api/brain", tags=["Planning"])


@router.post("/plan", response_model=PlanResponse, summary="Create an intelligent execution plan from user command")
@router.post("/api/brain/plan", response_model=PlanResponse, include_in_schema=False)
async def create_plan(payload: PlanRequest):
    """
    Accept text command in English, Urdu, or Roman Urdu,
    THINK, REASON, and ACT using phi3:mini,
    and return a structured step-by-step execution plan.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty")

    # Generate intelligent plan using phi3:mini non-blockingly
    result = await asyncio.to_thread(intelligent_plan, text)

    # Record context and task history
    try:
        context_service.add_command(
            text=text,
            intent=result.get("intent"),
            plan=result,
            metadata={"language": payload.language},
        )
        task_service.record_task(result)
    except Exception as e:
        logger.warning(f"Failed to record context/task history: {e}")

    return result
