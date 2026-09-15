from typing import Optional, Any, List
from pydantic import BaseModel, Field


class CreateFileRequest(BaseModel):
    name: str = Field(..., description="Name of the file including extension (e.g. test.txt)")
    location: str = Field(..., description="Target folder or predefined location keyword (e.g. desktop)")
    content: Optional[str] = Field("", description="Text content to write into the file")


class DeleteFileRequest(BaseModel):
    path: str = Field(..., description="Full path or relative path to file to delete")


class MoveFileRequest(BaseModel):
    source: str = Field(..., description="Source file path")
    destination: str = Field(..., description="Destination directory or full file path")


class CopyFileRequest(BaseModel):
    source: str = Field(..., description="Source file path")
    destination: str = Field(..., description="Destination directory or full file path")


class CreateFolderRequest(BaseModel):
    name: str = Field(..., description="Name of the folder to create")
    location: str = Field(..., description="Parent location keyword or directory path")


class OpenFileRequest(BaseModel):
    path: str = Field(..., description="Full path to file to open in system default application")


class SearchFileRequest(BaseModel):
    query: str = Field(..., description="Search keyword/term or file pattern")
    location: str = Field(..., description="Location keyword or directory to search in")


class FileItem(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int
    modified_time: str
    extension: Optional[str] = None


class FileOperationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class FileListResponse(BaseModel):
    success: bool
    location: str
    total: int
    items: List[FileItem]


class FileSearchResponse(BaseModel):
    success: bool
    query: str
    location: str
    total: int
    results: List[FileItem]


class ExecutePlanRequest(BaseModel):
    steps: List[dict] = Field(..., description="Steps from Brain API plan to execute")


class ExecutePlanResponse(BaseModel):
    status: str
    steps_executed: int
    steps_failed: int
    results: List[Any] = []
    message: Optional[str] = None

