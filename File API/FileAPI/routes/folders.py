from fastapi import APIRouter, HTTPException, status
from models.schemas import CreateFolderRequest, FileOperationResponse
from services import file_service

router = APIRouter(prefix="/api/folders", tags=["Folders"])


@router.post("/create", response_model=FileOperationResponse, status_code=status.HTTP_201_CREATED)
def create_folder_endpoint(req: CreateFolderRequest):
    try:
        data = file_service.create_folder(name=req.name, location=req.location)
        return FileOperationResponse(
            success=True,
            message=f"Folder '{req.name}' created successfully in '{req.location}'",
            data=data
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except OSError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error creating folder: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
