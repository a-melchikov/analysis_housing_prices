import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth


class WebDriverSetup:
    """
    Class WebDriverSetup is responsible for setting up the Chrome WebDriver using Selenium.

    Attributes:
        options (Options): Chrome options.
        headless (bool): Whether to run the browser in headless mode or not.
    """

    def __init__(self, headless=True):
        """
        Initializes an instance of the WebDriverSetup class.

        Args:
            headless (bool, optional): Whether to run the browser in headless mode or not. Defaults to True.
        """
        self.options = Options()
        self.options.add_argument("start-maximized")
        self.options.add_argument("--no-sandbox")
        if headless:
            self.options.add_argument("--headless")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_argument("--disable-blink-features=AutomationControlled")

    def setup_driver(self):
        """
        Method setup_driver creates and returns an instance of the Chrome WebDriver with configured parameters.

        Returns:
            WebDriver: An instance of the Chrome WebDriver.
        """
        driver = webdriver.Chrome(
            options=self.options, service=Service(log_path=os.devnull)
        )
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """
            },
        )
        return driver
