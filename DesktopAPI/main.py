import time
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import PORT, HOST, BRAIN_API_URL
from models.schemas import ExecutePlanRequest, APIResponse, PlanStep
from routes import apps_router, system_router, screen_router
from services.app_service import open_app, close_app
from services.system_service import handle_volume, capture_screenshot, handle_power
from services.screen_service import type_text, click_at, scroll_screen
from services.history_service import record_action

app = FastAPI(
    title="ARIA Desktop API",
    description="Desktop automation API for the ARIA system running on Port 8003",
    version="1.0.0",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(apps_router)
app.include_router(system_router)
app.include_router(screen_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "desktop_api",
        "port": PORT,
        "brain_api_url": BRAIN_API_URL,
    }


def execute_single_step(step: PlanStep) -> Dict[str, Any]:
    action = step.action.strip().lower()
    params = step.params or {}
    target = getattr(step, "target", None) or params.get("target")

    # Map aliases from intelligent planner
    if action == "open_notepad":
        action = "open_app"
        params["app"] = "notepad"
    elif action == "open_calculator":
        action = "open_app"
        params["app"] = "calc"
    elif action == "open_explorer":
        action = "open_app"
        params["app"] = "explorer"
    elif action in ["take_screenshot", "screenshot"]:
        action = "screenshot"
    elif action == "volume_up":
        action = "volume"
        params["action"] = "up"
    elif action == "volume_down":
        action = "volume"
        params["action"] = "down"
    elif action == "mute":
        action = "volume"
        params["action"] = "mute"
    elif action in ["lock_screen", "lock"]:
        action = "power"
        params["action"] = "lock"
        params["confirm"] = True
    elif action == "shutdown":
        action = "power"
        params["action"] = "shutdown"
        params["confirm"] = True
    elif action == "restart":
        action = "power"
        params["action"] = "restart"
        params["confirm"] = True
    elif action in ["type_text", "type"]:
        action = "type"
        if target and not params.get("text"):
            params["text"] = target

    if action in ["open_app", "app_open", "app/open"]:
        app_name = params.get("app") or target or ""
        success, message = open_app(app_name)
        record_action("execute_plan_step:open_app", params, success, {"message": message})
        return {"action": action, "success": success, "message": message}

    elif action in ["close_app", "app_close", "app/close"]:
        app_name = params.get("app") or target or ""
        success, message = close_app(app_name)
        record_action("execute_plan_step:close_app", params, success, {"message": message})
        return {"action": action, "success": success, "message": message}

    elif action in ["volume", "system_volume", "system/volume"]:
        vol_action = params.get("action", "up")
        level = params.get("level")
        success, message = handle_volume(vol_action, level)
        record_action("execute_plan_step:volume", params, success, {"message": message})
        return {"action": action, "success": success, "message": message}

    elif action in ["screenshot", "system_screenshot", "system/screenshot"]:
        save_to = params.get("save_to", "desktop")
        success, message, file_path = capture_screenshot(save_to)
        record_action("execute_plan_step:screenshot", params, success, {"file_path": file_path, "message": message})
        return {"action": action, "success": success, "message": message, "file_path": file_path}

    elif action in ["power", "system_power", "system/power"]:
        power_action = params.get("action", "")
        confirm = params.get("confirm", False)
        success, message = handle_power(power_action, confirm=confirm)
        record_action("execute_plan_step:power", params, success, {"message": message})
        return {"action": action, "success": success, "message": message}

    elif action in ["type", "screen_type", "screen/type"]:
        text = params.get("text") or target or ""
        speed = params.get("speed", "normal")
        success, message = type_text(text, speed=speed)
        record_action("execute_plan_step:type", params, success, {"message": message})
        return {"action": action, "success": success, "message": message}

    elif action in ["click", "screen_click", "screen/click"]:
        x = params.get("x", 0)
        y = params.get("y", 0)
        button = params.get("button", "left")
        success, message = click_at(x, y, button=button)
        record_action("execute_plan_step:click", params, success, {"message": message})
        return {"action": action, "success": success, "message": message}

    elif action in ["scroll", "screen_scroll", "screen/scroll"]:
        direction = params.get("direction", "down")
        amount = params.get("amount", 3)
        success, message = scroll_screen(direction=direction, amount=amount)
        record_action("execute_plan_step:scroll", params, success, {"message": message})
        return {"action": action, "success": success, "message": message}

    elif action in ["wait", "sleep"]:
        seconds = float(params.get("seconds", 1.0))
        time.sleep(seconds)
        record_action("execute_plan_step:wait", params, True, {"seconds": seconds})
        return {"action": action, "success": True, "message": f"Waited for {seconds} second(s)"}

    else:
        msg = f"Unsupported plan action: '{action}'"
        record_action("execute_plan_step:unknown", params, False, {"message": msg})
        return {"action": action, "success": False, "message": msg}


@app.post("/api/desktop/execute-plan", response_model=APIResponse, tags=["Plan Execution"])
async def execute_plan(plan: ExecutePlanRequest):
    if not plan.steps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "No steps provided in plan", "data": None},
        )

    results: List[Dict[str, Any]] = []
    overall_success = True

    for idx, step in enumerate(plan.steps):
        step_result = execute_single_step(step)
        step_result["step_index"] = idx
        results.append(step_result)
        if not step_result.get("success", False):
            overall_success = False

    record_action(
        "execute_plan_summary",
        {"total_steps": len(plan.steps)},
        overall_success,
        {"results": results},
    )

    return APIResponse(
        success=overall_success,
        message=f"Executed {len(plan.steps)} steps with overall success: {overall_success}",
        data={"results": results},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
