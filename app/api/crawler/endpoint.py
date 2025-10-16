from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.service import start_crawling, push_to_crm

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
    keyword: str
):
    return StreamingResponse(
        start_crawling(keyword),
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