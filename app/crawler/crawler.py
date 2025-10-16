from abc import ABC
from crawl4ai import JsonCssExtractionStrategy, CrawlerRunConfig
from crawl4ai import  AsyncWebCrawler, BrowserConfig, LLMExtractionStrategy, LLMConfig
from typing import Any
from .login import QianLiMaLoginStrategy
from pydantic import BaseModel
from app.utils import create_event

class Contact(BaseModel):
    name: str
    telphone: str

class Content(BaseModel):
    summaried_content: str

class Crawler(ABC):
    def __init__(
            self, login_strategy: QianLiMaLoginStrategy, base_url: str,
            headless: bool, verbose: bool, session_id: str
        ):
        super().__init__()
        self.base_url = base_url
        self.login_strategy = login_strategy
        self.crawler = AsyncWebCrawler(
            config=BrowserConfig(
                headless=headless,
                verbose=verbose,
                use_persistent_context=True,
                use_managed_browser=True,
                user_data_dir="./cached_user_profile",
                viewport_height=1080,
                viewport_width=1920
            )
        )
        self.crawler.crawler_strategy.set_hook(
            'on_page_context_created',
            self.login_strategy.login
        )
        self._started = False
        self.session_id = session_id

    async def __aenter__(self):
        await self.crawler.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.crawler.__aexit__(exc_type, exc_val, exc_tb)
    
    async def start(self):
        if self._started:
            return
        await self.crawler.start()
        self._started = True

    async def close(self):
        if not self._started:
            return False
        result = await self.crawler.close()
        self._started = False
        return result


class QianLiMaCrawler(Crawler):
    def __init__(
            self, login_strategy: QianLiMaLoginStrategy,
            base_url: str = "https://qiye.qianlima.com",
            headless: bool = True, verbose: bool = True,
            session_id: str = None
        ):
        super().__init__(
            login_strategy = login_strategy,
            base_url = base_url,
            headless = headless,
            verbose = verbose,
            session_id = session_id
        )

    async def get_detail_head(self, query_url: str) -> Any:
        """
        Get project info from head.

        Return:
            json str:
            [
                {
                    "title": "2025年广东产互新型工业化...",
                    "type": "招标公告",
                    "area": "广东-广州-海珠区",
                    "date": "2025/09/10"
                }
            ]
        """
        schema = {
            "name": "detail_head",
            "baseSelector": "#printInfo-head > div > div",
            "fields": [
                {"name": "title", "selector": ".long-project-name > div", "type": "text"},
                {"name": "type", "selector": ".long-project-property > .long-project-property-left > span:nth-child(1)", "type": "text"},
                {"name": "area", "selector": ".long-project-property > .long-project-property-left > span:nth-child(2)", "type": "text"},
                {"name": "date", "selector": ".long-project-property > .long-project-property-left > span:nth-child(3)", "type": "text"}
            ]
        }
        strategy = JsonCssExtractionStrategy(schema)
        config = CrawlerRunConfig(
            session_id=self.session_id,
            extraction_strategy=strategy
        )

        content_result = await self.crawler.arun(url=query_url, config=config)

        return content_result.extracted_content
    
    async def close_detail(self, query_url: str) -> Any:
        click_for_close="""
        const selector = ".tags-view-item.active .el-icon-close";
        const element = document.querySelector(selector);
        element.click()
        """
        close_config = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=click_for_close,
            js_only=True
        )

        await self.crawler.arun(query_url, config=close_config)

    
    async def _get_redirected_url(self, query_url: str) -> Any:
        #STEP 1: Get all conten item divs in current page
        get_child_divs = """
        const parentDiv = document.querySelector('.page-default-list .list');
        const childDivs = parentDiv.querySelectorAll('.list-card.list-item');
        const count = childDivs.length;
        window.childDivs = childDivs;
        return count;
        """
        config = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=get_child_divs,
            js_only=True
        )
        result = await self.crawler.arun(query_url, config=config)
        child_divs_count = result.js_execution_result.get("results")[0]

        #STEP 2: Iterate each content item
        for LOOP in range(child_divs_count):
            click_child = """
            window.childDivs[LOOP].click();
            """.replace("LOOP", str(LOOP))
            wait_for_close = """js:() => {
                const selector = ".tags-view-item.active .el-icon-close";
                const element = document.querySelector(selector);
                if (element) {
                    return true;
                }
                return false;
            }"""
            child_config = CrawlerRunConfig(
                session_id=self.session_id,
                js_code=click_child,
                wait_for=wait_for_close,
                js_only=True
            )
            await self.crawler.arun(query_url, config=child_config)

            #STEP 3: Click content item and get the redirected url
            get_redirected_url = """
            return window.location.href;
            """
            get_redirected_config = CrawlerRunConfig(
                session_id=self.session_id,
                js_code=get_redirected_url,
                js_only=True
            )
            result_for_url = await self.crawler.arun(query_url, config=get_redirected_config)
            redirected_url = result_for_url.js_execution_result.get("results")[0]

            #STEP 4: Click button for contact detail
            await self._setup_detail_new(redirected_url)

            yield create_event("get_redirected_url", redirected_url)

    async def _setup_page(self, query_url: str, keyword, area=None, scope=None) -> None:
        """Initialize page on first load, typically search with keyword."""

        wait_for_input = "css:.search-input input"
        config1 = CrawlerRunConfig(
            session_id=self.session_id,
            wait_for=wait_for_input
        )
        await self.crawler.arun(query_url,config=config1)

        search_for = """
        const input = document.querySelector('.search-input input');
        input.value = 'SEARCH_KEYWORD_PLACEHOLDER';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        """
        wait_for_button = "css:.search-btn"
        config2 = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=search_for.replace('SEARCH_KEYWORD_PLACEHOLDER', keyword),
            wait_for=wait_for_button,
            js_only=True
        )
        await self.crawler.arun(query_url,config=config2)

        click_button = """
        const searchBtn = document.querySelector('.search-btn');
        searchBtn.click();
        """
        wait_for_publish_time = "css:.select-filters-wrap div:nth-child(3) .right-option-box > div:nth-child(2)"
        config3 = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=click_button,
            wait_for=wait_for_publish_time,
            js_only=True
        )
        await self.crawler.arun(query_url,config=config3)

        click_publish_time = """
        const publishTime = document.querySelector('.select-filters-wrap div:nth-child(3) .right-option-box > div:nth-child(2)');
        publishTime.click();
        """
        wait_for_item = "css:.list > div:first-child .title-flex > div"
        config4 = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=click_publish_time,
            wait_for=wait_for_item,
            js_only=True
        )
        await self.crawler.arun(query_url,config=config4)

        get_current_title = """
        const firstTitle = document.querySelector('.list > div:first-child .title-flex > div');
        const currentTitle = firstTitle.textContent.trim();
        if (!window.currentPageTitle) {
            window.currentPageTitle = currentTitle;
        }
        """
        config5 = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=get_current_title,
            js_only=True
        )
        await self.crawler.arun(query_url,config=config5)

        return
    
    async def _setup_detail_new(self,  query_url: str) -> str:
        wait_for_button = "css:#printInfo .project-contacts-content > div:last-child"
        wait_for_button_config =CrawlerRunConfig(
            session_id=self.session_id,
            wait_for=wait_for_button,
            wait_for_timeout=3000,
            js_only=True
        )
        await self.crawler.arun(query_url, config=wait_for_button_config)

        """Click [查看联系人详情] for detail if button existed"""
        click_for_more = """
        const click_for_more_selector = '#printInfo .project-contacts-content > div:last-child';
        const click_for_more_element = document.querySelector(click_for_more_selector);
        if (click_for_more_element) {
            click_for_more_element.click();
            window.click_for_more = click_for_more_element;
        }
        """
        wait_for_drawer = """js:() => {
            if (!window.click_for_more) {
                return true;
            }
        
            const drawer_selector = '#app > div > section > div > div > section > div > div.drawer.el-drawer > div > div > div > div.drawer-body'
            const drawer = document.querySelector(drawer_selector);
            if (drawer) {
                window.click_for_more = null;
                return true;
            }

            window.click_for_more.click()
            const drawer_after_click = document.querySelector(drawer_selector);
            if (drawer_after_click) {
                window.click_for_more = null;
                // window.delayStartTime = null;
                return true;
            }

            return false
        }"""

        config = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=click_for_more,
            wait_for=wait_for_drawer,
            js_only=True
        )
        await self.crawler.arun(query_url, config=config)

        return

    async def _is_last_page(self, query_url: str) -> bool:
        """
        Check if it's the last page based on the presence of a specified element
        """

        check_for_element = """
        const selector = '.next-btn.icon-aright';
        const element = document.querySelector(selector);
        if (!element) return "yes";

        const isDisabled = t1.disabled;
        if (isDisabled) return "yes";

        return "no";
        """
        config = CrawlerRunConfig(
            session_id=self.session_id,
            js_code=check_for_element,
            js_only=True
        )

        result = await self.crawler.arun(query_url, config=config)
        return result.js_execution_result.get("results")[0]
    
    async def get_detail_abstract(self, query_url: str) -> Any:
        """
        Get info from [正文摘要].
        
        Return:
            json str:
            [
                {
                    "project_number": "BS-01-26-B",
                    "estimated_amount": "405.00万元",
                    "bidding_org": "BS-01-26-B",
                    "agency": "肇庆市公共资源交易中...",
                    "registration_ddl": "2025年09月26日",
                    "bidding_ddl": "2025年10月15日"
                }
            ]
        """
        schema = {
            "name": "detail_abstract",
            "baseSelector": "#printInfo .project-detail .card-content .table",
            "fields": [
                {"name": "project_number", "selector": "div:nth-child(1) > div:nth-child(2)", "type": "text"},
                {"name": "estimated_amount", "selector": "div:nth-child(1) > div:nth-child(4)", "type": "text"},
                {"name": "bidding_org", "selector": "div:nth-child(2) > div:nth-child(2) > span:nth-child(1) > span > span", "type": "text"},
                {"name": "agency", "selector": "div:nth-child(2) > div:nth-child(4) > span:nth-child(1)", "type": "text"},
                {"name": "registration_ddl", "selector": "div:nth-child(3) > div:nth-child(2)", "type": "text"},
                {"name": "bidding_ddl", "selector": "div:nth-child(3) > div:nth-child(4)", "type": "text"}
            ]
        }
        strategy = JsonCssExtractionStrategy(schema)
        config = CrawlerRunConfig(extraction_strategy=strategy)

        content_result = await self.crawler.arun(url=query_url, config=config)

        return content_result.extracted_content
    
    async def get_detail_content(self, query_url: str) -> Any:
        """
        Get info from [公告内容].
        
        Return:
            json str:
            [
                {
                    "summaried_content": "肇庆鼎湖区两....",
                    "error": false
                }
            ]
        """
        llm_strategy = LLMExtractionStrategy(
            llm_config = LLMConfig(
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                provider="openai/qwen-plus",
                api_token="env:ALI_API_KEY"
            ),
            schema=Content.model_json_schema(),
            extraction_type="schema",
            instruction="请对招标内容进行总结, 主要关注于招标的物品, 项目等内容, 控制字数在300字以内. 忽略联系人, 地址, 电话, 条款, 注意事项, 条款等信息.",
            apply_chunking=False,
            input_format="markdown",
            extra_args={"temperature": 1.0}
        )

        config = CrawlerRunConfig(
            session_id=self.session_id,
            css_selector=".project-detail-content",
            extraction_strategy=llm_strategy
        )
        detail_content = await self.crawler.arun(url=query_url,config=config)
        return detail_content.extracted_content

    async def get_detail_contact(self, query_url: str):
        """
        Get the contact info for the fist tel number that is not masked.

        Return:
            json str:
            [
                {
                    "name": "张先生",
                    "telphone": "0758-1234657",
                    "error": false
                }
            ]
        """
        llm_strategy = LLMExtractionStrategy(
            llm_config = LLMConfig(
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                provider="openai/qwen-plus",
                api_token="env:ALI_API_KEY"
            ),
            schema=Contact.model_json_schema(),
            extraction_type="schema",
            instruction="请提取其中第一个手机号码不带星号的联系人名称(可以为'暂未公布')以及对应的手机号码, 如果没有手机号码满足条件, 就获取座机号码. 仅需返回一位即可.",
            apply_chunking=False,
            input_format="markdown",
            extra_args={"temperature": 1.0}
        )

        config = CrawlerRunConfig(
            session_id=self.session_id,
            css_selector=".el-drawer .drawer-body",
            extraction_strategy=llm_strategy
        )
        detail_contact = await self.crawler.arun(url=query_url, config=config)
        return detail_contact.extracted_content

    async def iterate_search_results(
            self, keyword: str = None,
            area: str = None, scope: str = None
    ):
        """
        After search, query contetn items and their detail one by one
        with page turning.
        """
        query_url_suffix = "/new_qd_yfbsite/#/infoCenter/search"
        query_url = self.base_url + query_url_suffix

        # Process the first page
        await self._setup_page(query_url=query_url, keyword=keyword)
        async for event in self._get_redirected_url(query_url=query_url):
            yield event

        if await self._is_last_page(query_url) == "yes":
            yield create_event("done")
            return
        
        js_next_page = """
        const selector = '.next-btn.icon-aright';
        const button = document.querySelector(selector);
        if (button) button.click();
        """

        wait_for_more = """js:() => {
            // Check if page has changed by comparing the first item's title
            const firstTitle = document.querySelector('.list > div:first-child .title-flex > div');
            
            if (!firstTitle) {
                return false;
            }
            
            const currentTitle = firstTitle.textContent.trim();
            
            if (currentTitle !== window.currentPageTitle) {
                window.currentPageTitle = currentTitle;
                return true;
            }

            return false;
        }"""
        while True:
            config_next = CrawlerRunConfig(
                session_id=self.session_id,
                js_code=js_next_page,
                wait_for=wait_for_more,
                js_only=True,
            )

            await self.crawler.arun(query_url, config=config_next)
            async for event in self._get_redirected_url(query_url=query_url):
                yield event

            if await self._is_last_page(query_url) == "yes":
                yield create_event("done")
                break
        return