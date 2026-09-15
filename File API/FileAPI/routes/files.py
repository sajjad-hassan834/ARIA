from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from models.schemas import (
    CreateFileRequest,
    DeleteFileRequest,
    MoveFileRequest,
    CopyFileRequest,
    OpenFileRequest,
    SearchFileRequest,
    FileOperationResponse,
    FileListResponse,
    FileSearchResponse,
    ExecutePlanRequest,
    ExecutePlanResponse,
)
from services import file_service

router = APIRouter(prefix="/api/files", tags=["Files"])


@router.post("/create", response_model=FileOperationResponse, status_code=status.HTTP_201_CREATED)
def create_file_endpoint(req: CreateFileRequest):
    try:
        data = file_service.create_file(name=req.name, location=req.location, content=req.content)
        return FileOperationResponse(
            success=True,
            message=f"File '{req.name}' created successfully in '{req.location}'",
            data=data
        )
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error creating file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/delete", response_model=FileOperationResponse)
def delete_file_endpoint(req: DeleteFileRequest):
    try:
        data = file_service.delete_file(path=req.path)
        return FileOperationResponse(
            success=True,
            message=f"File/path '{req.path}' deleted successfully",
            data=data
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Safety Check Blocked: {str(e)}")
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error deleting file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/move", response_model=FileOperationResponse)
def move_file_endpoint(req: MoveFileRequest):
    try:
        data = file_service.move_file(source=req.source, destination=req.destination)
        return FileOperationResponse(
            success=True,
            message="File moved successfully",
            data=data
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error moving file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/copy", response_model=FileOperationResponse)
def copy_file_endpoint(req: CopyFileRequest):
    try:
        data = file_service.copy_file(source=req.source, destination=req.destination)
        return FileOperationResponse(
            success=True,
            message="File copied successfully",
            data=data
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error copying file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/list", response_model=FileListResponse)
def list_files_endpoint(
    location: str = Query("desktop", description="Location alias (desktop, downloads, documents, etc.) or path"),
    extension: Optional[str] = Query(None, description="Optional extension filter (e.g. pdf, txt)")
):
    try:
        items = file_service.list_files(location=location, extension=extension)
        return FileListResponse(
            success=True,
            location=location,
            total=len(items),
            items=items
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error listing files: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/open", response_model=FileOperationResponse)
def open_file_endpoint(req: OpenFileRequest):
    try:
        data = file_service.open_file(path=req.path)
        return FileOperationResponse(
            success=True,
            message=f"File '{req.path}' opened in system default application",
            data=data
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error opening file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/search", response_model=FileSearchResponse)
def search_files_endpoint(req: SearchFileRequest):
    try:
        results = file_service.search_files(query=req.query, location=req.location)
        return FileSearchResponse(
            success=True,
            query=req.query,
            location=req.location,
            total=len(results),
            results=results
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error searching files: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/execute-plan", response_model=ExecutePlanResponse)
def execute_plan_endpoint(req: ExecutePlanRequest):
    results = []
    failed = 0
    executed = 0
    for idx, step in enumerate(req.steps):
        action = step.get("action", "").lower().strip()
        params = step.get("params") or step
        try:
            if action in ["create_file", "file_create"]:
                res = file_service.create_file(
                    name=params.get("name", "untitled.txt"),
                    location=params.get("location", "desktop"),
                    content=params.get("content", ""),
                )
            elif action in ["delete_file", "file_delete"]:
                target_path = params.get("target") or params.get("path") or params.get("query")
                res = file_service.delete_file(path=target_path)
            elif action in ["move_file", "file_move"]:
                res = file_service.move_file(
                    source=params.get("source") or params.get("query", ""),
                    destination=params.get("destination") or params.get("target", ""),
                )
            elif action in ["copy_file", "file_copy"]:
                res = file_service.copy_file(
                    source=params.get("source") or params.get("query", ""),
                    destination=params.get("destination") or params.get("target", ""),
                )
            elif action in ["create_folder", "folder_create"]:
                res = file_service.create_folder(
                    name=params.get("name", "New Folder"),
                    location=params.get("location", "desktop"),
                )
            elif action in ["open_file", "file_open"]:
                res = file_service.open_file(
                    path=params.get("path") or params.get("target") or params.get("query", "")
                )
            else:
                res = {"action": action, "status": "simulated", "step": idx}
            results.append({"step": idx, "action": action, "result": res})
            executed += 1
        except Exception as e:
            failed += 1
            results.append({"step": idx, "action": action, "error": str(e)})

    return ExecutePlanResponse(
        status="success" if failed == 0 else ("partial" if executed > 0 else "error"),
        steps_executed=executed,
        steps_failed=failed,
        results=results,
        message=f"Executed {executed} steps, {failed} failed."
    )

