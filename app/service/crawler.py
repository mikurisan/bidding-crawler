import asyncio
from app.crawler.crawler import QianLiMaLoginStrategy, QianLiMaCrawler
from app.utils import parse_sse_event, create_event
from app.repositories import QianlimaBiddingDetailHeadRepository
from app.repositories import QianlimaBiddingDetailAbstractRepository
from app.repositories import QianlimaBiddingDetailContentRepository
from app.repositories import QianlimaBiddingDetailContactRepository

crawler_lock = asyncio.Lock()

async def start_crawling(
    keyword: str
):
    if crawler_lock.locked():
        yield create_event("error", "The crawler currently is running, try again later!")
        return

    async with crawler_lock:
        qianlima_login = QianLiMaLoginStrategy()
        
        async with QianLiMaCrawler(
            login_strategy=qianlima_login,
            headless=True,
            session_id = "qianlima"
        ) as crawler:
            async for sse_event in crawler.iterate_search_results(keyword=keyword):
                event, data = parse_sse_event(sse_event)

                if event == "done":
                    yield sse_event
                    return

                if event == "get_redirected_url":
                    redirected_url = data.get("content")

                detail_head = await crawler.get_detail_head(redirected_url)
                with QianlimaBiddingDetailHeadRepository() as head_repo:
                    created_ids = head_repo.create_records_from_json(detail_head, redirected_url)

                    if not created_ids:
                        await crawler.close_detail(redirected_url)
                        continue

                detail_abstract = await crawler.get_detail_abstract(redirected_url)
                with QianlimaBiddingDetailAbstractRepository() as abstract_repo:
                    abstract_repo.create_records_from_json(detail_abstract, created_ids[0])

                detail_content = await crawler.get_detail_content(redirected_url)
                with QianlimaBiddingDetailContentRepository() as content_repo:
                    content_repo.create_records_from_json(detail_content, created_ids[0])

                detail_contact = await crawler.get_detail_contact(redirected_url)
                with QianlimaBiddingDetailContactRepository() as contact_repo:
                    contact_repo.create_records_from_json(detail_contact, created_ids[0])

                yield create_event("created_record", created_ids[0])

                await crawler.close_detail(redirected_url)