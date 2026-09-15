from fastapi import APIRouter, HTTPException, status
from models.schemas import VolumeRequest, ScreenshotRequest, PowerRequest, APIResponse
from services.system_service import handle_volume, capture_screenshot, handle_power
from services.history_service import record_action

router = APIRouter(prefix="/api/desktop/system", tags=["System"])


@router.post("/volume", response_model=APIResponse)
async def adjust_volume(req: VolumeRequest):
    success, message = handle_volume(req.action, req.level)
    record_action("system_volume", {"action": req.action, "level": req.level}, success, {"message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"action": req.action, "level": req.level})


@router.post("/screenshot", response_model=APIResponse)
async def take_screenshot(req: ScreenshotRequest):
    save_to = req.save_to or "desktop"
    success, message, file_path = capture_screenshot(save_to)
    record_action("system_screenshot", {"save_to": save_to}, success, {"file_path": file_path, "message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"file_path": file_path})


@router.post("/power", response_model=APIResponse)
async def power_control(req: PowerRequest):
    action_lower = req.action.strip().lower()
    if action_lower in ["shutdown", "restart"] and not req.confirm:
        msg = f"Safety confirmation required for {action_lower}. Please provide 'confirm': true."
        record_action("system_power", {"action": req.action, "confirm": req.confirm}, False, {"message": msg})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": msg, "data": None},
        )

    success, message = handle_power(req.action, req.confirm or False)
    record_action("system_power", {"action": req.action, "confirm": req.confirm}, success, {"message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"action": req.action})
