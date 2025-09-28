from fastapi import Request
from app.crawler import CrawlerManager

def get_crawler_manager(request: Request) -> CrawlerManager:
    return request.app.state.crawler_manager