from fastapi import APIRouter, HTTPException, status
from models.schemas import ScreenTypeRequest, ScreenClickRequest, ScreenScrollRequest, APIResponse
from services.screen_service import type_text, click_at, scroll_screen
from services.history_service import record_action

router = APIRouter(prefix="/api/desktop/screen", tags=["Screen Automation"])


@router.post("/type", response_model=APIResponse)
async def screen_type(req: ScreenTypeRequest):
    speed = req.speed or "normal"
    success, message = type_text(req.text, speed=speed)
    record_action("screen_type", {"text": req.text, "speed": speed}, success, {"message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"length": len(req.text), "speed": speed})


@router.post("/click", response_model=APIResponse)
async def screen_click(req: ScreenClickRequest):
    button = req.button or "left"
    success, message = click_at(req.x, req.y, button=button)
    record_action("screen_click", {"x": req.x, "y": req.y, "button": button}, success, {"message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"x": req.x, "y": req.y, "button": button})


@router.post("/scroll", response_model=APIResponse)
async def screen_scroll(req: ScreenScrollRequest):
    direction = req.direction or "down"
    amount = req.amount if req.amount is not None else 3
    success, message = scroll_screen(direction=direction, amount=amount)
    record_action("screen_scroll", {"direction": direction, "amount": amount}, success, {"message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"direction": direction, "amount": amount})
