from fastapi import FastAPI
from app.core import setup_logger
from app.api import crawler_router
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

setup_logger()

app = FastAPI()
app.include_router(crawler_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

DOWNLOAD_DIR = Path(os.getenv('DOWNLOAD_DIR'))
DOWNLOAD_DIR.mkdir(exist_ok=True)
app.mount("/download", StaticFiles(directory=str(DOWNLOAD_DIR)), name="download")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2026)