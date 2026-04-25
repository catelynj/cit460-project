"""
server.py — Raspberry Pi Camera File Transfer Server
Serves captured images/videos to a Flutter mobile app over WiFi (HTTP).
Run alongside main.py: `python server.py`
"""

import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# config

CAPTURES_DIR = Path("/home/c8win/Captures")       
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
VIDEO_EXTENSIONS = {".mp4", ".h264", ".mkv"}
HOST = "0.0.0.0"                              
PORT = 8000

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Pi Camera Server",
    description="Transfer images and videos from Raspberry Pi to Flutter app",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=str(CAPTURES_DIR)), name="files")


def file_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    return "unknown"


def file_info(path: Path) -> dict:
    stat = path.stat()
    return {
        "filename": path.name,
        "type": file_type(path),
        "size_bytes": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "url": f"/files/{path.name}",
        "download_url": f"/download/{path.name}",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "captures_dir": str(CAPTURES_DIR)}


@app.get("/media")
async def list_media(
    type: Optional[str] = Query(None, description="Filter by 'image' or 'video'"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    all_files = sorted(
        [
            p for p in CAPTURES_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in (IMAGE_EXTENSIONS | VIDEO_EXTENSIONS)
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if type in ("image", "video"):
        all_files = [p for p in all_files if file_type(p) == type]

    paginated = all_files[offset : offset + limit]

    return {
        "total": len(all_files),
        "offset": offset,
        "limit": limit,
        "items": [file_info(p) for p in paginated],
    }


@app.get("/media/latest")
async def get_latest(type: Optional[str] = Query(None, description="'image' or 'video'")):
    files = sorted(
        [
            p for p in CAPTURES_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in (IMAGE_EXTENSIONS | VIDEO_EXTENSIONS)
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if type in ("image", "video"):
        files = [p for p in files if file_type(p) == type]

    if not files:
        raise HTTPException(status_code=404, detail="No captures found")

    return file_info(files[0])


@app.get("/download/{filename}")
async def download_file(filename: str):
    # Sanitize: prevent path traversal
    safe_name = Path(filename).name
    file_path = CAPTURES_DIR / safe_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File '{safe_name}' not found")

    media_type = (
        "image/jpeg" if file_path.suffix.lower() in {".jpg", ".jpeg"}
        else "image/png" if file_path.suffix.lower() == ".png"
        else "video/mp4" if file_path.suffix.lower() == ".mp4"
        else "application/octet-stream"
    )

    logger.info(f"Serving file: {safe_name} ({file_path.stat().st_size} bytes)")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_name,
    )


@app.delete("/media/{filename}")
async def delete_file(filename: str):
    safe_name = Path(filename).name
    file_path = CAPTURES_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{safe_name}' not found")

    file_path.unlink()
    logger.info(f"Deleted: {safe_name}")
    return {"deleted": safe_name}


@app.delete("/media")
async def delete_all_media(background_tasks: BackgroundTasks):
    def _delete_all():
        count = 0
        for p in CAPTURES_DIR.iterdir():
            if p.is_file() and p.suffix.lower() in (IMAGE_EXTENSIONS | VIDEO_EXTENSIONS):
                p.unlink()
                count += 1
        logger.info(f"Bulk delete complete: {count} files removed")

    background_tasks.add_task(_delete_all)
    return {"message": "Deletion started in background"}

if __name__ == "__main__":
    logger.info(f"Starting Pi Camera Server on http://{HOST}:{PORT}")
    logger.info(f"Captures directory: {CAPTURES_DIR}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")