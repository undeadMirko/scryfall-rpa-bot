import os
import time
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from src.logger import logger
from src.utils import retry

class ScryfallBot:
    """
    RPA Bot to interact with Scryfall website using Selenium.
    Extracts card information such as price, set, and rarity.
    """

    def __init__(self, headless: bool = True):
        logger.info("Initializing ScryfallBot...")
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--window-size=1920,1080")
        
        # Check if we are running inside Docker with Alpine Chromium
        chrome_bin = os.getenv("CHROME_BIN")
        chrome_driver_path = os.getenv("CHROME_DRIVER")
        
        if chrome_bin and chrome_driver_path:
            self.options.binary_location = chrome_bin
            self.service = Service(executable_path=chrome_driver_path)
        else:
            self.service = Service(ChromeDriverManager().install())
            
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
            self.driver.implicitly_wait(5)
            logger.info("Selenium WebDriver initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def _take_screenshot(self, name: str) -> None:
        """Saves a screenshot to the logs directory for debugging."""
        os.makedirs("logs/screenshots", exist_ok=True)
        timestamp = int(time.time())
        filepath = f"logs/screenshots/{name}_{timestamp}.png"
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Could not take screenshot: {e}")

    @retry(max_retries=3, delay=2, backoff=2)
    def search_card(self, card_name: str) -> Optional[Dict[str, str]]:
        """
        Searches for a card by name and extracts its details.
        Uses exponential backoff for retries.
        """
        logger.info(f"Searching for card: '{card_name}'")
        try:
            # Scryfall exact search URL
            search_url = f"https://scryfall.com/search?q=!'{card_name}'"
            self.driver.get(search_url)
            
            # Wait for either the card page or the 'No cards found' message
            wait = WebDriverWait(self.driver, 10)
            
            # Check if card was found
            if "No cards found" in self.driver.page_source:
                logger.warning(f"Card '{card_name}' not found on Scryfall.")
                return None
            
            # Explicit wait for the card details container
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-text-title")))
            
            # Extract data
            name_element = self.driver.find_element(By.CLASS_NAME, "card-text-title")
            extracted_name = name_element.text.strip()
            
            # Set and rarity
            prints_element = self.driver.find_element(By.CLASS_NAME, "prints-current-set-name")
            set_info = prints_element.text.strip()
            
            # Price (USD)
            try:
                price_element = self.driver.find_element(By.XPATH, "//a[contains(@href, 'buy') and contains(text(), 'USD')]")
                price = price_element.text.strip().replace("USD", "").strip()
            except NoSuchElementException:
                price = "N/A"
                
            logger.info(f"Successfully extracted data for '{card_name}'.")
            return {
                "Searched Name": card_name,
                "Found Name": extracted_name,
                "Set & Rarity": set_info,
                "Price USD": price
            }

        except TimeoutException as e:
            logger.error(f"Timeout while searching for '{card_name}'.")
            self._take_screenshot(f"timeout_{card_name.replace(' ', '_')}")
            raise e
        except WebDriverException as e:
            logger.error(f"WebDriver exception while searching for '{card_name}': {e}")
            self._take_screenshot(f"error_{card_name.replace(' ', '_')}")
            raise e

    def close(self) -> None:
        """Closes the browser."""
        logger.info("Closing WebDriver...")
        if self.driver:
            self.driver.quit()
