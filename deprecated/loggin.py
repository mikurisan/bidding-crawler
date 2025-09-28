
from abc import ABC, abstractmethod
from playwright.async_api import Page, BrowserContext

import logging
import ddddocr

logger = logging.getLogger(__name__)


class LoginStrategy(ABC):
    def __init__(self, login_url, user_name, password):
        self.login_url = login_url
        self.user_name = user_name
        self.password = password

    @abstractmethod
    async def login(self, page: Page, context: BrowserContext, **kwargs):
        pass


class ChinazbzcLogin(LoginStrategy):
    """
    采购招标综合网 - 模拟登陆
    """
    def __init__(
            self, user_name, password,
            login_url="https://www.chinazbzc.com/index/index/login"
            ):
        super().__init__(
            login_url=login_url,
            user_name=user_name,
            password=password
            )
    
    async def login(self, page: Page, context: BrowserContext, **kwargs):
        try:
            await page.goto(self.login_url)
            await page.wait_for_selector("input[id='user_name']", timeout=10000)
            await page.wait_for_selector("input[id='password']", timeout=10000)

            await page.fill("input[id='user_name']", self.user_name)
            await page.fill("input[id='password']", self.password)

            await page.click("button[type='submit'].log")
            await page.wait_for_timeout(10000)

            logger.info(f"Redirect to page: {page.url}")
            if "member" in page.url:
                logger.info("Login successful")
            else:
                logger.warning("Login may failed due to not redirect to the specified url")
        except Exception as e:
            logger.error(f"Login failed with error: {e}")


class Jy365TradeLogin(LoginStrategy):
    """
    中招联合 - 模拟登陆
    """
    def __init__(
            self, user_name, password,
            login_url="https://jy.365trade.com.cn/wb_bidder/static/dist/index"
            ):
        super().__init__(
            login_url=login_url,
            user_name=user_name,
            password=password
            )
        self._ocr = ddddocr.DdddOcr()
        
    async def login(self, page: Page, context: BrowserContext, **kwargs):
        try:
            await page.goto(self.login_url)
            await page.wait_for_selector("input[id='username']", timeout=10000)
            await page.wait_for_selector("input[id='password']", timeout=10000)
            await page.wait_for_selector("#fm1 > div:nth-child(7) > img", timeout=10000)

            captcha_img = await page.query_selector("#fm1 > div:nth-child(7) > img")
            captcha_screenshot = await captcha_img.screenshot()
            verification_code = self._ocr.classification(captcha_screenshot)

            await page.fill("input[id='username']", self.user_name)
            await page.fill("input[id='password']", self.password)
            await page.fill("input[id='captcha']", verification_code)

            await page.click("#submit")
            await page.wait_for_timeout(2000)

            logging.info(f"Redirect to page: {page.url}")
            if "wb_bidder" in page.url:
                logger.info("Login successful")
            else:
                logger.warning("Login may failed due to not redirect to the specified url")

        except Exception as e:
            logger.error(f"Login failed with error: {e}")