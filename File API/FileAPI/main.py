import sys
from pathlib import Path

# Ensure FileAPI root is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import PORT, BRAIN_API_URL
from routes import files_router, folders_router

app = FastAPI(
    title="ARIA File API",
    description="File & Directory Management Microservice for ARIA System",
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

# Mount Routers
app.include_router(files_router)
app.include_router(folders_router)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "ARIA File API",
        "port": PORT,
        "brain_api_url": BRAIN_API_URL,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)

