import time
import logging
import random
import os

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

# Optional: load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class TLSContactSteps:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # -----------------------------
    # Telegram helpers
    # -----------------------------

    def telegram_send_message(self, text: str) -> bool:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            logger.warning("Telegram env vars missing: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            r = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=15)
            if r.status_code != 200:
                logger.warning(f"Telegram sendMessage failed: {r.status_code} {r.text}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Telegram sendMessage error: {e}")
            return False

    def telegram_send_photo(self, photo_path: str, caption: str = "") -> bool:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            logger.warning("Telegram env vars missing: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
            return False

        if not os.path.exists(photo_path):
            logger.warning(f"Screenshot not found: {photo_path}")
            return False

        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        try:
            with open(photo_path, "rb") as f:
                files = {"photo": f}
                data = {"chat_id": chat_id, "caption": caption}
                r = requests.post(url, data=data, files=files, timeout=30)

            if r.status_code != 200:
                logger.warning(f"Telegram sendPhoto failed: {r.status_code} {r.text}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Telegram sendPhoto error: {e}")
            return False

    # -----------------------------
    # Utilities
    # -----------------------------

    def human_delay(self, min_sec=1, max_sec=3):
        time.sleep(random.uniform(min_sec, max_sec))

    def remove_url_bar_focus(self):
        try:
            self.driver.execute_script("""
                if (document.body) {
                    document.body.focus();
                    document.body.click();
                }
            """)
            self.driver.execute_script("""
                var firstInput = document.querySelector('input, button, div, body');
                if (firstInput) {
                    firstInput.focus();
                    firstInput.blur();
                }
            """)
            self.human_delay(0.5, 1)
            logger.debug("URL bar focus removed")
            return True
        except Exception as e:
            logger.warning(f"Could not remove URL bar focus: {e}")
            return False

    def ensure_page_focus(self):
        try:
            self.remove_url_bar_focus()
            self.driver.execute_script("""
                if (document.body) {
                    document.body.focus();
                    document.body.click();
                    var visibleElement = document.querySelector('input, button, a, div[tabindex]');
                    if (visibleElement && visibleElement.offsetParent !== null) {
                        visibleElement.focus();
                        visibleElement.blur();
                    }
                }
            """)
            self.human_delay(0.3, 0.6)
            logger.debug("Page focus ensured")
            return True
        except Exception as e:
            logger.warning(f"Could not ensure page focus: {e}")
            return False

    def clear_email_field_focus(self, selector, by=By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )

            self.driver.execute_script("""
                arguments[0].blur();
                arguments[0].value = '';
            """, element)

            body = self.driver.find_element(By.TAG_NAME, 'body')
            body.click()
            self.human_delay(0.3, 0.6)

            element.click()
            self.human_delay(0.3, 0.6)

            element.send_keys(Keys.COMMAND + "a" if os.name == 'posix' else Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            self.human_delay(0.2, 0.4)

            logger.debug("Email field focus cleared")
            return True
        except Exception as e:
            logger.warning(f"Could not clear email field focus: {e}")
            return False

    def safe_click(self, selector, by=By.CSS_SELECTOR, timeout=10):
        try:
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            actions = ActionChains(self.driver)
            actions.move_to_element(element).pause(random.uniform(0.2, 0.5)).click().perform()

            self.human_delay(0.5, 1.5)
            return True
        except Exception as e:
            logger.warning(f"Could not click {selector}: {e}")
            return False

    def safe_click_by_xpath(self, xpath, timeout=10):
        try:
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            actions = ActionChains(self.driver)
            actions.move_to_element(element).pause(random.uniform(0.2, 0.5)).click().perform()

            self.human_delay(0.5, 1.5)
            return True
        except Exception as e:
            logger.warning(f"Could not click XPath {xpath}: {e}")
            return False

    def safe_type(self, selector, text, by=By.CSS_SELECTOR, timeout=10):
        try:
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            self.driver.execute_script("""
                arguments[0].setAttribute('autocomplete', 'off');
                arguments[0].setAttribute('autocorrect', 'off');
                arguments[0].setAttribute('autocapitalize', 'off');
                arguments[0].setAttribute('spellcheck', 'false');
                arguments[0].value = '';
            """, element)

            element.click()
            self.human_delay(0.3, 0.7)

            element.send_keys(Keys.COMMAND + "a" if os.name == 'posix' else Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            self.human_delay(0.2, 0.5)

            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.03, 0.1))

            self.human_delay(0.5, 1)
            return True
        except Exception as e:
            logger.warning(f"Could not type in {selector}: {e}")
            return False

    def safe_type_email(self, selector, text, by=By.CSS_SELECTOR, timeout=10):
        try:
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            self.driver.execute_script("""
                arguments[0].setAttribute('autocomplete', 'off');
                arguments[0].setAttribute('autocorrect', 'off');
                arguments[0].setAttribute('autocapitalize', 'off');
                arguments[0].setAttribute('spellcheck', 'false');
                arguments[0].value = '';
            """, element)

            self.driver.execute_script("arguments[0].blur();", element)
            self.human_delay(0.2, 0.4)

            element.click()
            self.human_delay(0.3, 0.7)

            element.send_keys(Keys.COMMAND + "a" if os.name == 'posix' else Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            self.human_delay(0.2, 0.5)

            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.03, 0.1))

            self.human_delay(0.5, 1)
            self.driver.execute_script("arguments[0].blur();", element)

            return True
        except Exception as e:
            logger.warning(f"Could not type email in {selector}: {e}")
            return False

    def wait_for_page_load(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.human_delay(1.5, 3.0)
            self.remove_url_bar_focus()
            self.ensure_page_focus()
            return True
        except Exception:
            logger.warning("Page load timeout")
            return False

    def wait_for_url_contains(self, url_part, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(url_part))
            logger.info(f"Successfully reached page containing: {url_part}")
            self.wait_for_page_load()
            return True
        except TimeoutException:
            logger.error(f"Timeout waiting for URL to contain: {url_part}")
            return False

    def wait_until_app_domain(self, prefix="https://visas-fr.tlscontact.com/en-us/", timeout=60):
        try:
            def on_app_prefix(driver):
                url = driver.current_url or ""
                if "auth/realms" in url:
                    return False
                return url.startswith(prefix)

            WebDriverWait(self.driver, timeout).until(on_app_prefix)
            logger.info(f"Returned to app domain. URL: {self.driver.current_url}")

            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//*[contains(., 'Select') or contains(@href,'workflow') or contains(@href,'service-level')]"
                    ))
                )
                logger.info("Post-login page marker detected (list/workflow link).")
            except TimeoutException:
                logger.warning("Post-login marker not detected yet; proceeding anyway.")

            self.wait_for_page_load()
            return True
        except TimeoutException:
            logger.error(
                f"Did not reach app domain with prefix: {prefix} within {timeout}s. "
                f"Current URL: {self.driver.current_url}"
            )
            return False

    def take_screenshot(self, filename):
        try:
            if os.path.exists(filename):
                os.remove(filename)
                logger.info(f"Deleted existing screenshot: {filename}")
        except Exception as e:
            logger.warning(f"Could not delete existing screenshot: {e}")

        self.driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")

    def check_if_already_on_target_page(self):
        current_url = self.driver.current_url
        return "workflow/service-level" in current_url or "/workflow" in current_url

    # -----------------------------
    # Enhanced CAPTCHA handler methods
    # -----------------------------

    def simulate_human_mouse_movement(self):
        """Simulate human-like mouse movements"""
        try:
            # Get current mouse position
            start_x = random.randint(100, 500)
            start_y = random.randint(100, 500)

            # Create human-like mouse movement
            actions = ActionChains(self.driver)

            # Move mouse in small random patterns
            for i in range(random.randint(2, 4)):
                offset_x = random.randint(-30, 30)
                offset_y = random.randint(-20, 20)
                duration = random.uniform(0.1, 0.3)
                actions.move_by_offset(offset_x, offset_y).pause(duration)

            actions.perform()
            self.human_delay(0.2, 0.5)

        except Exception:
            pass

    def move_mouse_like_human(self, element):
        """Move mouse to element with human-like motion"""
        try:
            # Get element location
            location = element.location
            size = element.size

            # Calculate target position (slightly random within element)
            target_x = location['x'] + random.randint(size['width'] // 4, size['width'] * 3 // 4)
            target_y = location['y'] + random.randint(size['height'] // 4, size['height'] * 3 // 4)

            # Create curved mouse movement
            actions = ActionChains(self.driver)

            # Start from random position
            start_x = random.randint(50, 200)
            start_y = random.randint(50, 200)
            actions.move_by_offset(start_x, start_y)

            # Create slight curve in movement
            mid_x = (start_x + target_x) // 2 + random.randint(-20, 20)
            mid_y = (start_y + target_y) // 2 + random.randint(-15, 15)

            # Move with varying speed
            actions.move_by_offset(mid_x - start_x, mid_y - start_y).pause(random.uniform(0.05, 0.15))
            actions.move_by_offset(target_x - mid_x, target_y - mid_y).pause(random.uniform(0.05, 0.15))

            actions.perform()
            self.human_delay(0.1, 0.3)

        except Exception:
            # Fallback to simple movement
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()

    def human_click(self, element):
        """Click with human-like behavior"""
        try:
            actions = ActionChains(self.driver)

            # Slight hesitation before click
            actions.pause(random.uniform(0.05, 0.15))

            # Click with slight mouse down/up timing variation
            actions.click_and_hold(element).pause(random.uniform(0.05, 0.1))
            actions.release(element)

            actions.perform()

            # Small random delay after click
            time.sleep(random.uniform(0.1, 0.3))

        except Exception:
            # Fallback to regular click
            element.click()

    def check_for_image_challenge(self):
        """Check if image selection challenge appeared"""
        try:
            # Look for image grid or image selection elements
            image_challenge_selectors = [
                "//div[contains(@class, 'rc-imageselect')]",
                "//div[contains(text(), 'Select all')]",
                "//img[contains(@src, 'image') and contains(@alt, 'CAPTCHA')]",
                "//div[@role='heading' and contains(text(), 'image')]",
            ]

            for xpath in image_challenge_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements and any(el.is_displayed() for el in elements):
                        logger.warning(f"Image challenge detected: {xpath}")
                        return True
                except Exception:
                    continue

            return False

        except Exception:
            return False

    def handle_captcha_challenge(self, timeout=15):
        """
        Enhanced CAPTCHA handler with human-like behavior simulation.
        """
        logger.info("🛡️ Checking for CAPTCHA iframe...")

        try:
            # Look for different CAPTCHA iframes
            iframe_xpaths = [
                "//iframe[contains(@title, 'challenge') or contains(@title, 'CAPTCHA')]",
                "//iframe[contains(@src, 'recaptcha') or contains(@src, 'captcha')]",
                "//iframe[contains(@src, 'google.com/recaptcha')]",
                "//iframe[@role='presentation']",
                "//iframe[starts-with(@src, 'https://www.google.com/recaptcha')]"
            ]

            captcha_iframe = None
            for xpath in iframe_xpaths:
                try:
                    captcha_iframe = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    logger.info(f"Found CAPTCHA iframe with XPath: {xpath}")
                    break
                except TimeoutException:
                    continue

            if not captcha_iframe:
                logger.info("ℹ️ No CAPTCHA iframe detected.")
                return False

            # Switch to CAPTCHA iframe
            self.driver.switch_to.frame(captcha_iframe)
            logger.info("➡️ Focus switched to CAPTCHA iframe.")

            # Simulate human-like mouse movement before clicking
            self.simulate_human_mouse_movement()

            # Try to find and click the checkbox
            checkbox_found = False

            # Try multiple checkbox selectors
            checkbox_selectors = [
                (By.ID, "recaptcha-anchor"),
                (By.CLASS_NAME, "recaptcha-checkbox"),
                (By.CSS_SELECTOR, "div.recaptcha-checkbox-border"),
                (By.CSS_SELECTOR, "div.recaptcha-checkbox"),
                (By.CSS_SELECTOR, "span.recaptcha-checkbox"),
                (By.CSS_SELECTOR, "div[role='checkbox']"),
                (By.XPATH, "//div[@role='checkbox' or @aria-checked]"),
            ]

            for by, selector in checkbox_selectors:
                try:
                    checkbox = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((by, selector))
                    )

                    if checkbox.is_displayed() and checkbox.is_enabled():
                        logger.info(f"Found checkbox: {selector}")

                        # Simulate human hesitation before clicking
                        self.human_delay(0.8, 1.5)

                        # Move mouse to checkbox with human-like motion
                        self.move_mouse_like_human(checkbox)

                        # Click with slight random offset
                        self.human_click(checkbox)

                        checkbox_found = True
                        logger.info(f"✅ Clicked checkbox: {selector}")
                        break

                except Exception:
                    continue

            # Switch back to main content
            self.driver.switch_to.default_content()

            if checkbox_found:
                # Wait for CAPTCHA response (check if images appear)
                self.human_delay(3, 5)

                # Check if image selection challenge appeared
                if self.check_for_image_challenge():
                    logger.warning("⚠️ Image selection challenge appeared (CAPTCHA not solved)")
                    return False
                else:
                    logger.info("✅ CAPTCHA checkbox clicked successfully")
                    return True
            else:
                logger.info("ℹ️ No checkbox found in CAPTCHA iframe")
                return False

        except TimeoutException:
            logger.info("ℹ️ No CAPTCHA iframe detected within timeout.")
            self.driver.switch_to.default_content()
            return False
        except Exception as e:
            logger.warning(f"⚠️ CAPTCHA handler error: {e}")
            self.driver.switch_to.default_content()
            return False

    # -----------------------------
    # Steps (your existing flow)
    # -----------------------------

    def step1_click_book_appointment(self):
        logger.info("Step 1: Clicking 'Book an appointment' button...")
        self.remove_url_bar_focus()
        self.ensure_page_focus()
        self.human_delay(1, 2)

        selectors = [
            "button.TlsButton_tls-button__syUS5.TlsButton_--filled__1vb1H.TlsButton_primary__sPypD.TlsButton_--lg__ElLNd",
        ]
        for selector in selectors:
            if self.safe_click(selector):
                logger.info("Successfully clicked 'Book an appointment'")
                self.wait_for_page_load()
                return True

        xpaths = [
            "//button[contains(@class, 'TlsButton_tls-button__syUS5') and contains(., 'Book an appointment')]",
            "//button[contains(., 'Book an appointment')]",
        ]
        for xpath in xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("Successfully clicked 'Book an appointment' (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("Could not find 'Book an appointment' button")
        return False

    def step2_click_france_visas_yes(self):
        logger.info("Step 2: Clicking 'Yes' for France-Visas question...")
        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        selectors = ["button#btn-yes", "#btn-yes"]
        for selector in selectors:
            if self.safe_click(selector):
                logger.info("Successfully clicked 'Yes' for France-Visas question")
                self.wait_for_page_load()
                return True

        xpaths = ["//button[@id='btn-yes']"]
        for xpath in xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("Successfully clicked 'Yes' for France-Visas question (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("Could not find France-Visas 'Yes' button")
        return False

    def step3_click_tlscontact_yes(self):
        logger.info("Step 3: Clicking 'Yes' for TLScontact registration question...")
        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "button#btn-yes")
            if len(elements) >= 2:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elements[1])
                self.human_delay(0.3, 0.6)
                ActionChains(self.driver).move_to_element(elements[1]).pause(0.3).click().perform()
                logger.info("Successfully clicked second 'Yes' button")
                self.wait_for_page_load()
                return True
        except Exception:
            pass

        xpaths = ["(//button[@id='btn-yes'])[2]"]
        for xpath in xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("Successfully clicked 'Yes' for TLScontact question (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("Could not find TLScontact 'Yes' button")
        return False

    def step4_click_login_button(self):
        logger.info("Step 4: Clicking 'LOG IN' button...")
        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        selectors = ["span#btn-select-country", "#btn-select-country"]
        for selector in selectors:
            if self.safe_click(selector):
                logger.info("Successfully clicked 'LOG IN' button")
                self.wait_for_page_load()
                return True

        xpaths = ["//span[@id='btn-select-country']", "//span[contains(., 'LOG IN')]"]
        for xpath in xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("Successfully clicked 'LOG IN' button (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("Could not find 'LOG IN' button")
        return False

    def step5_enter_email(self):
        logger.info("Step 5: Entering email address...")
        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        email = os.getenv("TLS_EMAIL", "")

        selectors = [
            "input#email-input-field",
            "#email-input-field",
            "input[name='username']",
            "input[type='text'][name='username']",
            "input.tls-input[name='username']"
        ]

        for selector in selectors:
            try:
                self.clear_email_field_focus(selector)
                if self.safe_type_email(selector, email):
                    logger.info(f"Successfully entered email: {email}")
                    return True
            except Exception as e:
                logger.warning(f"Email selector {selector} failed: {e}")

        xpaths = ["//input[@id='email-input-field']", "//input[@name='username']"]
        for xpath in xpaths:
            if self.safe_type_email(xpath, email, By.XPATH):
                logger.info(f"Successfully entered email (XPath): {email}")
                return True

        logger.error("Could not find email input field")
        return False

    def step6_enter_password(self):
        logger.info("Step 6: Entering password...")
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        password = os.getenv("TLS_PASSWORD", "")

        selectors = [
            "input#password-input-field",
            "#password-input-field",
            "input[name='password']",
            "input[type='password']",
            "input.tls-input[name='password']"
        ]
        for selector in selectors:
            if self.safe_type(selector, password):
                logger.info("Successfully entered password")
                return True

        xpaths = ["//input[@id='password-input-field']", "//input[@name='password']", "//input[@type='password']"]
        for xpath in xpaths:
            if self.safe_type(xpath, password, By.XPATH):
                logger.info("Successfully entered password (XPath)")
                return True

        logger.error("Could not find password input field")
        return False

    def step7_click_login_submit(self):
        logger.info("Step 7: Clicking Login submit button...")
        self.remove_url_bar_focus()
        self.ensure_page_focus()
        self.human_delay(1, 2)

        selectors = ["button#btn-login", "#btn-login", "button.bg-primary-500"]
        for selector in selectors:
            if self.safe_click(selector):
                logger.info("Successfully clicked Login submit button")
                self.wait_for_page_load()
                return True

        xpaths = ["//button[@id='btn-login']", "//button[normalize-space()='Login']", "//button[contains(., 'Login')]"]
        for xpath in xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("Successfully clicked Login submit button (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("Could not find Login submit button")
        return False

    def step8_click_select_button(self):
        logger.info("Step 8: Clicking Select button (dynamic formGroupId)...")

        self.human_delay(2, 4)
        self.wait_for_page_load(timeout=30)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        try:
            buttons = WebDriverWait(self.driver, 25).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "button[name='formGroupId'][type='submit']")
                )
            )
        except TimeoutException:
            logger.error("No Select buttons found (button[name='formGroupId'][type='submit']).")
            return False

        target = None
        for b in buttons:
            try:
                if b.is_displayed() and b.text.strip().lower() == "select":
                    target = b
                    break
            except Exception:
                continue

        if target is None:
            for b in buttons:
                try:
                    if b.is_displayed():
                        target = b
                        break
                except Exception:
                    continue

        if target is None:
            logger.error("Found formGroupId submit buttons, but none are visible.")
            return False

        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
            self.human_delay(0.5, 1.2)
            ActionChains(self.driver).move_to_element(target).pause(random.uniform(0.2, 0.5)).click().perform()
            logger.info(f"✅ Clicked Select. formGroupId value={target.get_attribute('value')}")
            self.human_delay(2, 4)
            return True
        except Exception as e:
            logger.warning(f"ActionChains click failed: {e}")

        try:
            self.driver.execute_script("arguments[0].click();", target)
            logger.info(f"✅ Clicked Select via JS. formGroupId value={target.get_attribute('value')}")
            self.human_delay(2, 4)
            return True
        except Exception as e:
            logger.error(f"JS click also failed: {e}")
            return False

    def step9_wait_for_service_level_page(self):
        logger.info("Step 9: Waiting for service level page to load...")

        target_url_parts = ["workflow/service-level", "/workflow/"]
        for url_part in target_url_parts:
            if self.wait_for_url_contains(url_part, timeout=30):
                logger.info(f"Successfully reached service level page (matched: {url_part})")
                return True

        if self.check_if_already_on_target_page():
            logger.info("Already on service level page")
            return True

        logger.error("Failed to reach service level page")
        return False

    def step10_click_continue_button(self):
        logger.info("Step 10: Clicking Continue button...")
        self.human_delay(3, 5)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        continue_selectors = [
            "a#book-appointment-btn",
            "#book-appointment-btn",
            "a[data-testid='btn-book-appointment']",
            "a[href*='appointment-booking']",
        ]

        for selector in continue_selectors:
            if self.safe_click(selector):
                logger.info("Successfully clicked Continue button")
                self.wait_for_page_load()
                return True

        continue_xpaths = [
            "//a[@id='book-appointment-btn']",
            "//a[@data-testid='btn-book-appointment']",
            "//a[contains(@href, 'appointment-booking')]",
            "//a[contains(text(), 'Continue')]"
        ]
        for xpath in continue_xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("Successfully clicked Continue button (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("Could not find Continue button")
        return False

    def step11_check_appointment_availability(self):
        logger.info("Step 11: Checking appointment availability...")
        self.human_delay(3, 5)
        self.wait_for_page_load()
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        screenshot_path = "appointment_availability_check.png"
        self.take_screenshot(screenshot_path)

        no_slots_xpaths = [
            "//p[contains(@class, 'mb-2') and contains(@class, 'text-center') and contains(text(), 'appointment slots available')]",
            "//p[contains(text(), \"We currently don't have any appointment slots available\")]",
            "//p[contains(text(), 'appointment slots available')]"
        ]

        for xpath in no_slots_xpaths:
            try:
                no_slots_element = self.driver.find_element(By.XPATH, xpath)
                if no_slots_element.is_displayed():
                    logger.info("No appointment slots available message detected")
                    print("No time")
                    # Send ONLY to Telegram channel
                    self.telegram_send_message("❌ No time")
                    self.telegram_send_photo(screenshot_path, caption="No time - Screenshot")
                    return True
            except Exception:
                continue

        # If no "no slots" message found
        logger.info("Appointment slots appear to be available")
        print("Yes time")

        # Send ONLY to Telegram channel
        self.telegram_send_message("✅ Yes time")
        self.telegram_send_photo(screenshot_path, caption="Yes time - Screenshot")

        return True

    # -----------------------------
    # NEW STEP 12: Click next month button
    # -----------------------------

    def step12_click_next_month(self):
        """
        Step 12: Automatically find and click the next month button
        Example: <a data-testid="btn-next-month-available" ...>February 2026</a>
        """
        logger.info("Step 12: Looking for next month button...")
        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        # First try: Your specific selector from screenshot
        selector = "a[data-testid='btn-next-month-available']"

        try:
            # Wait for the button to be available
            next_month_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )

            # Get the month text (e.g., "February 2026")
            month_text = next_month_button.text
            logger.info(f"Found next month button: {month_text}")

            # Click it
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_month_button)
            self.human_delay(0.5, 1)
            next_month_button.click()

            logger.info(f"✅ Automatically clicked: {month_text}")
            self.wait_for_page_load()
            return True

        except TimeoutException:
            logger.info("No next month button found with specific selector, trying other methods...")

        # Second try: Look for any next month button
        alternative_selectors = [
            "a[data-testid*='next-month']",
            "a[href*='month=']",
            "button[data-testid*='next-month']",
            "a:contains('Next')",
            "button:contains('Next')",
        ]

        for alt_selector in alternative_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, alt_selector)
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text
                            if element_text and ('202' in element_text or 'Next' in element_text):
                                logger.info(f"Found alternative next month button: {element_text}")

                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                self.human_delay(0.5, 1)
                                element.click()

                                logger.info(f"✅ Clicked: {element_text}")
                                self.wait_for_page_load()
                                return True
                    except Exception:
                        continue
            except Exception:
                continue

        logger.info("No next month button found (already on last available month)")
        return False

    # -----------------------------
    # Main execution method (UPDATED)
    # -----------------------------

    def execute_all_steps(self):
        logger.info("Starting TLSContact automation sequence...")

        if not self.step1_click_book_appointment():
            return False
        if not self.step2_click_france_visas_yes():
            return False
        if not self.step3_click_tlscontact_yes():
            return False
        if not self.step4_click_login_button():
            return False
        if not self.step5_enter_email():
            return False
        if not self.step6_enter_password():
            return False

        time.sleep(2)
        self.handle_captcha_challenge()

        if not self.step7_click_login_submit():
            return False

        if not self.wait_until_app_domain(prefix="https://visas-fr.tlscontact.com/en-us/", timeout=60):
            return False

        if not self.check_if_already_on_target_page():
            if not self.step8_click_select_button():
                return False

        if not self.step9_wait_for_service_level_page():
            return False
        if not self.step10_click_continue_button():
            return False

        # Check current month's availability
        logger.info("=== Checking CURRENT month ===")
        if not self.step11_check_appointment_availability():
            return False

        # Try to check next month
        logger.info("=== Checking NEXT month ===")
        if self.step12_click_next_month():
            # Wait for next month to load
            self.wait_for_page_load()
            self.human_delay(2, 4)

            # Check availability in next month
            if not self.step11_check_appointment_availability():
                return False
        else:
            logger.info("No next month available to check")

        logger.info("🎉 All automation steps completed successfully!")
        return True