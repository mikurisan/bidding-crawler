from typing import Optional
from .crawler import QianLiMaCrawler
from .login import QianLiMaLoginStrategy
from datetime import datetime

class CrawlerManager:
    def __init__(self):
        self._crawler: Optional[QianLiMaCrawler] = None
        self._is_initialized = False
        self._start_time = None
        self._is_running = False
    
    def initialize_crawler(self):
        if not self._is_initialized:
            qianlima_login = QianLiMaLoginStrategy()
            self._crawler = QianLiMaCrawler(
                login_strategy=qianlima_login,
                headless=False,
                session_id = "qianlima"
            )
            self._is_initialized = True

    def _set_start_time(self, start_time: Optional[datetime] = None):
        if self._is_running:
            return False

        if start_time is None:
            self._start_time = datetime.now()
            return True
        
        self._start_time = start_time
        
        return True
    
    @property
    def execution_time(self):
        if not self._is_running:
            return -1
        
        current_time = datetime.now()
        time_delta = current_time - self._start_time
        total_seconds = int(time_delta.total_seconds())

        return total_seconds
    
    async def start_crawler(self):
        if not self._is_initialized:
            return False
        
        await self._crawler.start()

        self._set_start_time()
        self._is_running = True

        return True

    async def stop_crawler(self):
        if not self._is_initialized:
            return False
        
        await self._crawler.close()
        
        self._start_time = None
        self._is_running = False

        return True
    
    async def query_content_and_detail(self, keyword: str):
        async for event in self._crawler.iterate_search_results(keyword=keyword):
            yield event