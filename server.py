"""
server.py — Raspberry Pi Camera File Transfer Server
Serves captured images/videos to a Flutter mobile app over WiFi (HTTP).
Run alongside main.py: `python server.py`
"""

import os
import asyncio
import logging
from api import wolfram, translate
from pathlib import Path
from datetime import datetime
from typing import Optional
import sqlite3


from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# config

CAPTURES_DIR = Path("/home/c8win/Captures")       
IMAGE_EXTENSION = {".jpg"}
VIDEO_EXTENSION = {".h264"}
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
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=str(CAPTURES_DIR)), name="files")


def file_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSION:
        return "image"
    if ext in VIDEO_EXTENSION:
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

@app.get("/history")
async def get_history(limit: int = 50):
    conn = sqlite3.connect("/home/c8win/queries.db")
    rows = conn.execute(
        "SELECT query, response, status, queried_at FROM query_history ORDER BY queried_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [
        {"query": r[0], "response": r[1], "status": r[2], "queried_at": r[3]}
        for r in rows
    ]

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
            if p.is_file() and p.suffix.lower() in (IMAGE_EXTENSION | VIDEO_EXTENSION)
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
            if p.is_file() and p.suffix.lower() in (IMAGE_EXTENSION | VIDEO_EXTENSION)
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

if __name__ == "__main__":
    logger.info(f"Starting Pi Camera Server on http://{HOST}:{PORT}")
    logger.info(f"Captures directory: {CAPTURES_DIR}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")