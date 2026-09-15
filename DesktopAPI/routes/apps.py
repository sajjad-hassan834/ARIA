from fastapi import APIRouter, HTTPException, status
from models.schemas import AppActionRequest, APIResponse
from services.app_service import open_app, close_app
from services.history_service import record_action

router = APIRouter(prefix="/api/desktop/app", tags=["Applications"])


@router.post("/open", response_model=APIResponse)
async def open_application(req: AppActionRequest):
    success, message = open_app(req.app)
    record_action("app_open", {"app": req.app}, success, {"message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"app": req.app})


@router.post("/close", response_model=APIResponse)
async def close_application(req: AppActionRequest):
    success, message = close_app(req.app)
    record_action("app_close", {"app": req.app}, success, {"message": message})

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": message, "data": None},
        )

    return APIResponse(success=True, message=message, data={"app": req.app})
