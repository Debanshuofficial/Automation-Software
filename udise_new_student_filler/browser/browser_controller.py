from playwright.sync_api import sync_playwright, Browser, Page, Playwright
from typing import Optional, Tuple
from utils.logger import AppLogger

class BrowserController:
    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.connected = False

    def connect(self, endpoint_url: str = "http://localhost:9222") -> Tuple[bool, str]:
        """Connect to an existing Chrome instance via CDP."""
        import asyncio
        original_get_running_loop = getattr(asyncio, 'get_running_loop', None)
        def _mock_get_running_loop():
            if original_get_running_loop is not None:
                asyncio.get_running_loop = original_get_running_loop
            else:
                delattr(asyncio, 'get_running_loop')
            raise RuntimeError("no running event loop")
        asyncio.get_running_loop = _mock_get_running_loop
        
        try:
            self.playwright = sync_playwright().start()
            self.logger.info(f"Connecting to Chrome at {endpoint_url}...")
            self.browser = self.playwright.chromium.connect_over_cdp(endpoint_url)
            
            contexts = self.browser.contexts
            if not contexts:
                return False, "No browser contexts found."
                
            pages = contexts[0].pages
            if not pages:
                return False, "No active tabs found in Chrome."
                
            # Prefer a page that looks like UDISE+, otherwise just take the first one
            self.page = pages[0]
            for p in pages:
                if "udise" in p.url.lower() or "student" in p.url.lower():
                    self.page = p
                    break
                    
            self.connected = True
            self.logger.info("Chrome Connected")
            return True, "Successfully connected to Chrome."
            
        except Exception as e:
            self.connected = False
            error_msg = f"Failed to connect to Chrome: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        finally:
            if original_get_running_loop is not None:
                asyncio.get_running_loop = original_get_running_loop
            else:
                delattr(asyncio, 'get_running_loop')

    def disconnect(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.connected = False
        self.logger.info("Chrome Disconnected")

    def get_page(self) -> Optional[Page]:
        return self.page
