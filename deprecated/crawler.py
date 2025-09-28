from abc import ABC, abstractmethod
from urllib.parse import urlencode, quote, urlparse
from crawl4ai import JsonCssExtractionStrategy, CrawlerRunConfig, AsyncWebCrawler, BrowserConfig, CacheMode
from typing import List, Dict
from .login import QianLiMaLoginStrategy, LoginStrategy

import json
import re
import time
import math


class CrawlerStrategy(ABC):
    def __init__(self, base_url, crawler, crawler_run_config):
        self.base_url = base_url
        self.crawler = crawler
        self.crawler_run_config = crawler_run_config


class ChinazbzcCrawler(CrawlerStrategy):
    def __init__(
            self, crawler, crawler_run_config,
            base_url="https://www.chinazbzc.com"
            ):
        super().__init__(
            base_url = base_url,
            crawler = crawler,
            crawler_run_config = crawler_run_config
            )

    def _build_query_url(self, key_name=None, r_name=None, set_day=None, page=1) -> str:
        """
        构建一个模拟查询的 url

        params:
            key_name: 查询关键词
            r_name: 省份名称
            set_day: 查询范围 (month, day, week, year and all)
            page: 页数

        return:
            查询界面 url
        """
        base_url = self.base_url + "/index/index/search"
        
        params = {
            'KeyName': key_name or '',
            'r_name': r_name or '',
            'SetDay': set_day,
            'page': page
        }
        
        query_string = urlencode(params, quote_via=quote)
        
        return f"{base_url}?{query_string}"
    
    async def get_query_page_html(
            self, query_url,
            css_selector="#wrap > div.ny.w1100 > div.m_l.fl > div > div.catlist"
            ) -> str:
        """
        获取查询 url 界面的原生 html

        params:
            query_url: 查询界面的 url
            css_selector: 查询界面 item 对应的 css selector

        return:
            查询界面 item 的 raw html str
        """
        self.crawler_run_config.css_selector = css_selector
        raw_result = await self.crawler.arun(query_url, config=self.crawler_run_config)
    
        return raw_result.html

    async def _get_total_pages(self, raw_html) -> int:
        """
        获取查询界面的 page 总数

        params:
            raw_html: 网页原生 html

        return:
            page 总数
        """
        self.crawler_run_config.css_selector = None

        schema = {
            "name": "page_text",
            "baseSelector": "div.catlist div#page",
            "fields": [
                {"name": "page_text", "type": "text"}, 
            ],
        }
        strategy = JsonCssExtractionStrategy(schema)
        self.crawler_run_config.extraction_strategy = strategy
        page_result = await self.crawler.arun(
            url="raw://" + raw_html,
            config=self.crawler_run_config
        )

        page_text = json.loads(page_result.extracted_content)
        match = re.search(r'当前\s+\d+\s*/\s*(\d+)\s*页', page_text[0]["page_text"])
        total_pages = int(match.group(1))

        return total_pages
    
    async def _get_title_url_list(self, raw_html: str) -> List[Dict[str, str]]:
        """
        获取查询界面中所有标题对应的 url

        params:
            raw_html: 网页原生 html

        return:
            指定查询界面页数下所有标题对应的 url 组成的 list
        """
        self.crawler_run_config.css_selector = None
        schema = {
            "name": "url_list",
            "baseSelector": "div.catlist ul#search_box table li",
            "fields": [
                {"name": "link", "selector": "a.fl", "type": "attribute", "attribute": "href"},
            ]
        }
        strategy = JsonCssExtractionStrategy(schema)
        self.crawler_run_config.extraction_strategy = strategy
        url_result = await self.crawler.arun(
                url="raw://" + raw_html,
                config=self.crawler_run_config
            )
        url_list_pre = json.loads(url_result.extracted_content)
        url_list = [item['link'] for item in url_list_pre]

        return url_list
    
    async def get_page_content(
            self, url,
            css_selector="#wrap > div.ny.w1100 > div.m_l.fl > div.left_box2 > div > table"
            ) -> str:
        """
        获取指定页面的 content

        params:
            url: 指定页面的 url
            css_selector: 内容对应的 css selector

        return:
            符合 markdown 格式的内容 str
        """
        parsed = urlparse(url)
        is_complete_url = bool(parsed.scheme and parsed.netloc)
        base_url = url
        if not is_complete_url:
            base_url = self.base_url + url
        

        self.crawler_run_config.css_selector = css_selector
        content_result = await self.crawler.arun(base_url, config=self.crawler_run_config)

        return content_result.markdown

    async def query_all(self, keyword, area=None, scope="month") -> List[str]:
        """
        查询指定内容下的所有内容信息

        params:
            keyword: 关键字
            area: 地区
            scope: 范围
        return:
            每个页面的 content, 作为元素存储在 list 中
        """
        raw_query_url = self._build_query_url(key_name=keyword, r_name=area, set_day=scope)
        raw_html = await self.get_query_page_html(raw_query_url)
        total_pages = await self._get_total_pages(raw_html)
        time.sleep(2)

        query_url_list = []
        for page in range(total_pages):
            query_url = self._build_query_url(key_name=keyword, r_name=area, page=page+1)
            query_html = await self.get_query_page_html(query_url)
            
            url_list = await self._get_title_url_list(query_html)
            query_url_list.extend(url_list)

        content_list = []
        for url in query_url_list:
            content = await self.get_page_content(url)
            content_list.append(content)
            time.sleep(2)
            
        return content_list
    

class Jy365TradeCrawler(CrawlerStrategy):
    def __init__(
            self, crawler, crawler_run_config,
            base_url="https://jy.365trade.com.cn"
            ):
        super().__init__(
            base_url = base_url,
            crawler = crawler,
            crawler_run_config = crawler_run_config
            )

    async def _get_content_list(self, raw_html: str):
        self.crawler_run_config.css_selector = None

        schema = {
            "name": "content_list",
            "baseSelector": ""
        }

    async def query_all(self, keyword=None, area=None, scope=None):
        self.crawler_run_config.css_selector = "#main > div > div > div.resultCon > div.allContent"
        raw_result = await self.crawler.arun("https://jy.365trade.com.cn/wb_bidder/static/dist/seekProject", config=self.crawler_run_config)
        
        with open('output.html', 'w', encoding='utf-8') as file:
            file.write(raw_result.html)

        return True