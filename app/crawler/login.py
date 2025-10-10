from playwright.async_api import Page, BrowserContext
import logging

logger = logging.getLogger(__name__)

class QianLiMaLoginStrategy:
    def __init__(
            self, user_name: str=None, password: str=None,
            login_url: str="https://qiye.qianlima.com/yfbsite/a/login"
        ):
        self.user_name = user_name
        self.password = password
        self.login_url = login_url
        self._logged_in = False

    async def login(self, page: Page, context: BrowserContext, **kwargs):
        if self._logged_in:
                return

        try:
            await page.goto("https://qiye.qianlima.com/new_qd_yfbsite/#/infoCenter/search")
            
            # Handle popup
            try:
                await page.locator(".el-message-box__btns button").click(timeout=2000)
            except:
                pass

            # Check if logined
            await page.wait_for_timeout(timeout=2000)
            if "new_qd_yfbsite" in page.url:
                logger.info("Already logged in")
                self._logged_in = True
                return

            # Get QR code and Wait for login
            qr_img = page.locator("#qrcode > div.saomaWrap > img")
            if await qr_img.is_visible(timeout=2000):

                #TODO: 后期转为使用钉钉通知实现
                await qr_img.screenshot(path=r"/home/appuser/captcha.png")
                logger.info("QR code saved, waiting for scan...")

                await page.wait_for_url("**/new_qd_yfbsite/**", timeout=30000)
                self._logged_in = True
                logger.info("Login successful")
                await page.wait_for_timeout(timeout=2000)

        except TimeoutError:
            logger.warning("Login timeout")
        except Exception as e:
            logger.error(f"Login failed: {e}")