from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.crawler import CrawlerManager
from app.core import get_crawler_manager
from app.service import start_crawling, push_to_crm
from app.core import get_crawler_manager

router = APIRouter()

@router.get(
    "/get_crawl_results",
    response_model=None,
    responses={
        200: {
            "description": "Streaming response with crawl results",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    }
)
async def get_crawl_results(
    keyword: str,
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    return StreamingResponse(
        start_crawling(keyword, crawler_manager),
        media_type="text/event-stream"
    )

@router.get(
    "/push_clue",
    response_model=None,
    responses={
        200: {
            "description": "Streaming response with crawl results",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    }
)
async def push_clue():
    return StreamingResponse(
        push_to_crm(),
        media_type="text/event-stream"
    )