from app.crawler import CrawlerManager
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def create_instance(app: FastAPI):
    crawler_manager = CrawlerManager()
    crawler_manager.initialize_crawler()

    app.state.crawler_manager = crawler_manager
    yield

    await crawler_manager.stop_crawler()