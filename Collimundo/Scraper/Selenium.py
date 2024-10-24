"""file with basic functions useful for selenium"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class Selenium:


    def __init__(self):
        self.driver = webdriver.Chrome()


    def __del__(self):
        if self.driver:
            self.driver.quit()

    def scroll_up(self):
        """Scrolls all the way up"""
        # Scroll to the top of the page
        while True:
            # Get current scroll position
            initial_scroll_position = self.driver.execute_script("return window.scrollY;")

            # Scroll up by a fixed amount
            self.driver.execute_script("window.scrollBy(0, -1000);")

            # Wait for a short duration to allow the content to load
            time.sleep(0.1)  # Adjust as needed based on page loading speed

            # Check if scroll position has changed
            final_scroll_position = self.driver.execute_script("return window.scrollY;")

            # If the scroll position hasn't changed, it means we've reached the top of the page
            if final_scroll_position == initial_scroll_position or final_scroll_position == 0:
                break


    def scroll_down(self):
        # Get initial scroll height
        last_height = self.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to the bottom
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for the page to load
            time.sleep(0.1)  # Adjust as needed based on page loading speed

            # Calculate new scroll height and compare with last scroll height
            new_height = self.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Exit if no more scrolling possible
            last_height = new_height


