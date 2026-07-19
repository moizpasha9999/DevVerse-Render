import pandas as pd
import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time


class AutomationBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        

    def get_text(self, selector):
        """Return text content or None if element is missing."""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        except Exception:
            return None

    def get_attr(self, selector, attr):
        """Return attribute value or None if element is missing."""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector).get_attribute(attr)
        except Exception:
            return None

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless=new")

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.notifications": 2,
            "profile.managed_default_content_settings.geolocation": 2
        }

        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(version_main=150, options=options)
        wait = WebDriverWait(self.driver, 10)
        return driver, wait

    def run_automation(self, category, location, limit):
        t1 = time.time()

        
        try:
            self.driver.get("https://www.google.com/maps")

            # 1. Perform Search
            search_query = f"{category} in {location}"
            search_bar = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_bar.send_keys(search_query + Keys.ENTER)

            results_data = []
            seen_names = set()

            # 2. Results and Scrolling Logic
            count = 0
            while len(results_data) < limit:
                # Locate the results feed
                feed = WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
                )

                # Scroll action
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", feed
                )

                items = self.driver.find_elements(By.CLASS_NAME, "hfpxzc")

                for item in items[count:]:
                    if len(results_data) >= limit:
                        break

                    try:
                        item.click()

                        WebDriverWait(self.driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf'))
                        )

                        name = self.get_text("h1.DUwDvf") if (self.get_text("h1.DUwDvf")) else self.get_text("span.a5H0ec")

                        if name in seen_names:
                            continue

                        # 3. Collect Details
                        details = {
                            "full_name": name,
                            "rating": self.get_text("span.MW4etd"),
                            "review_count": self.get_text("span[aria-label*='reviews']"),
                            "address": self.get_text("button[data-item-id='address'] .Io6YTe"),
                            "website": self.get_attr("a[data-item-id='authority']", "href"),
                            "phone": self.get_text("button[data-item-id^='phone'] .Io6YTe"),
                            "menu_link": self.get_attr("a[data-item-id='menu']", "href"),
                            "link": item.get_attribute("href"),
                        }

                        links = self.driver.find_elements(By.TAG_NAME, 'a')
                        for link in links:
                            url = link.get_attribute('href')
                            if url and "facebook.com" in url:
                                details['facebook'] = url
                            elif url and "instagram.com" in url:
                                details['instagram'] = url
                            elif url and "whatsaap.com" in url:
                                details['whatsaap'] = url

                        results_data.append(details)
                        seen_names.add(name)
                        count += 1

                        # Wait for the original page to load again
                        self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
                        )


                        self.driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight", feed
                        )

                    except Exception:
                        continue

                # Scroll down to load more
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", feed
                )
                time.sleep(0.3)

            # 4. Format with Pandas
            
            t2 = time.time()
            return results_data, t2-t1
            

        except Exception as e:
            t2 = time.time()
            return f"Error: {e}", t2-t1

            

        


if __name__ == "__main__":
    bot = AutomationBot()
    bot.run_automation()