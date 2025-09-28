import asyncio
import time
import json

from .login import ChinazbzcLogin, Jy365TradeLogin, QianLiMaLoginStrategy
from .crawler import ChinazbzcCrawler, Jy365TradeCrawler, QianLiMaCrawler
from .logger_config import setup_logger
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def chinazgbc():

    session_id = "chinazgbc"

    crawler_run_config = CrawlerRunConfig(
        js_code="window.scrollTo(0, document.body.scrollHeight);",
        wait_for="body",
        delay_before_return_html=3.0,
        session_id=session_id
    )

    chinazbzc_login = ChinazbzcLogin("xxx", "xxx")

    crawler = AsyncWebCrawler()
    crawler.crawler_strategy.set_hook('on_page_context_created', chinazbzc_login.login)
    time.sleep(2)

    await crawler.start()

    chinazbzc_crawler = ChinazbzcCrawler(crawler=crawler, crawler_run_config=crawler_run_config)
    raw_html = await chinazbzc_crawler.query_all("传奇", "上海")
    print(raw_html)

    await crawler.close()


async def jy365trade():

    session_id = "jy365trade"
    browser_conf = BrowserConfig(headless=False)

    crawler_run_config = CrawlerRunConfig(
        js_code="window.scrollTo(0, document.body.scrollHeight);",
        wait_for="body",
        delay_before_return_html=3.0,
        session_id=session_id
    )

    jy365trade_login = Jy365TradeLogin("xxx", "xxx")

    crawler = AsyncWebCrawler(config=browser_conf)
    crawler.crawler_strategy.set_hook('on_page_context_created', jy365trade_login.login)
    time.sleep(2)

    await crawler.start()
    
    jy365trade_crawler = Jy365TradeCrawler(crawler=crawler, crawler_run_config=crawler_run_config)
    raw_markdown = await jy365trade_crawler.query_all()
    print(raw_markdown)

    await crawler.close()


if __name__ == "__main__":
    setup_logger()
    asyncio.run(qianlima())