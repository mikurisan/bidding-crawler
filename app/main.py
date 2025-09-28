from fastapi import FastAPI
from app.core import setup_logger
from app.core import create_instance
from app.api import crawler_router
import uvicorn

setup_logger()

app = FastAPI(lifespan=create_instance)
app.include_router(crawler_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2026)