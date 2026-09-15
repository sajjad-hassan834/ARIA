from fastapi import APIRouter, HTTPException
from models.schemas import ClassifyRequest, ClassifyResponse
from services.planner_service import planner_service

router = APIRouter(prefix="/api/brain", tags=["Classification"])


@router.post("/classify", response_model=ClassifyResponse, summary="Classify text to target API and action")
async def classify_text(payload: ClassifyRequest):
    """
    Accept text input and return which API should handle it along with target port, action, and parameters.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty")

    classification = planner_service.classify(text)
    return classification
