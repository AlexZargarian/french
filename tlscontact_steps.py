import time
import logging
import random
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TLSContactSteps:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # -----------------------------
    # Utilities
    # -----------------------------

    def human_delay(self, min_sec=1, max_sec=3):
        """Add human-like random delays"""
        time.sleep(random.uniform(min_sec, max_sec))

    def remove_url_bar_focus(self):
        """Remove focus from URL bar to eliminate vertical bar in address bar"""
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
        """Ensure focus is on the page, not the URL bar"""
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
        """Clear any vertical bar/cursor from email field"""
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
        """Safely click an element with waiting and retry"""
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
        """Safely click an element using XPath"""
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
        """Safely type text into an input field"""
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
        """Safely type email with extra blur/focus handling"""
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
        """Wait for page to fully load"""
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
        """Wait until current URL contains specific text"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(url_part))
            logger.info(f"Successfully reached page containing: {url_part}")
            self.wait_for_page_load()
            return True
        except TimeoutException:
            logger.error(f"Timeout waiting for URL to contain: {url_part}")
            return False

    def wait_until_app_domain(self, prefix="https://visas-fr.tlscontact.com/en-us/", timeout=60):
        """Wait until we're redirected back to the TLS app domain after login."""
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
        """Take screenshot of current state and delete existing one"""
        try:
            if os.path.exists(filename):
                os.remove(filename)
                logger.info(f"Deleted existing screenshot: {filename}")
        except Exception as e:
            logger.warning(f"Could not delete existing screenshot: {e}")

        self.driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")

    def check_if_already_on_target_page(self):
        """Check if we're already on the service level page"""
        current_url = self.driver.current_url
        return "workflow/service-level" in current_url or "/workflow" in current_url

    # -----------------------------
    # Steps
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

        xpaths = [
            "//button[@id='btn-yes']",
        ]
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

                actions = ActionChains(self.driver)
                actions.move_to_element(elements[1]).pause(0.3).click().perform()

                logger.info("Successfully clicked second 'Yes' button")
                self.wait_for_page_load()
                return True
        except Exception:
            pass

        xpaths = [
            "(//button[@id='btn-yes'])[2]",
        ]
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

        xpaths = [
            "//span[@id='btn-select-country']",
            "//span[contains(., 'LOG IN')]",
        ]
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

        email = os.getenv("TLS_EMAIL", "Info@i-travel.net")

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

        xpaths = [
            "//input[@id='email-input-field']",
            "//input[@name='username']",
        ]
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

        password = os.getenv("TLS_PASSWORD", "Zar4ka055?")

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

        xpaths = [
            "//input[@id='password-input-field']",
            "//input[@name='password']",
            "//input[@type='password']"
        ]
        for xpath in xpaths:
            if self.safe_type(xpath, password, By.XPATH):
                logger.info("Successfully entered password (XPath)")
                return True

        logger.error("Could not find password input field")
        return False

    def handle_captcha_challenge(self, timeout=12):
        """Detects and clicks the 'I am not a robot' checkbox inside its iframe."""
        logger.info("🛡️ Checking for 'I am not a robot' checkbox...")
        try:
            iframe_xpath = (
                "//iframe[contains(@title, 'challenge') "
                "or contains(@src, 'captcha') "
                "or contains(@title, 'reCAPTCHA')]"
            )

            captcha_iframe = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, iframe_xpath))
            )

            self.driver.switch_to.frame(captcha_iframe)
            logger.info("➡️ Focus switched to CAPTCHA iframe.")

            checkbox_selectors = [
                (By.ID, "recaptcha-anchor"),          # Google reCAPTCHA
                (By.CSS_SELECTOR, ".mark"),           # Cloudflare Turnstile
                (By.CSS_SELECTOR, "input[type='checkbox']"),
                (By.CLASS_NAME, "ctp-checkbox-label"),
            ]

            clicked = False
            for by, sel in checkbox_selectors:
                try:
                    checkbox = self.driver.find_element(by, sel)
                    if checkbox.is_displayed() and checkbox.is_enabled():
                        self.human_delay(0.6, 1.4)

                        actions = ActionChains(self.driver)
                        actions.move_to_element(checkbox).pause(
                            random.uniform(0.2, 0.5)
                        ).click().perform()

                        logger.info(f"✅ Clicked checkbox locator (ActionChains): {sel}")
                        clicked = True
                        break
                except Exception:
                    continue

            if clicked:
                time.sleep(5)

            self.driver.switch_to.default_content()
            return clicked

        except TimeoutException:
            logger.info("ℹ️ No checkbox detected within timeout.")
            self.driver.switch_to.default_content()
            return False
        except Exception as e:
            logger.warning(f"⚠️ CAPTCHA handler error: {e}")
            self.driver.switch_to.default_content()
            return False

    def step7_click_login_submit(self):
        """Final submit on the auth page (pressed AFTER CAPTCHA)."""
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

        xpaths = [
            "//button[@id='btn-login']",
            "//button[normalize-space()='Login']",
            "//button[contains(., 'Login')]"
        ]
        for xpath in xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("Successfully clicked Login submit button (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("Could not find Login submit button")
        return False

    def step8_click_select_button(self):
        """
        Step 8: Click the Select button on travel-groups page.
        FIX: do NOT hardcode value='23012573' because it changes (you saw 24313450).
        """
        logger.info("Step 8: Clicking Select button (dynamic formGroupId)...")

        self.human_delay(2, 4)
        self.wait_for_page_load(timeout=30)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        # Wait until at least one submit button for formGroupId exists
        try:
            buttons = WebDriverWait(self.driver, 25).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "button[name='formGroupId'][type='submit']")
                )
            )
        except TimeoutException:
            logger.error("No Select buttons found (button[name='formGroupId'][type='submit']).")
            return False

        # Prefer visible button with text "Select"
        target = None
        for b in buttons:
            try:
                if b.is_displayed() and b.text.strip().lower() == "select":
                    target = b
                    break
            except Exception:
                continue

        # Fallback: first visible
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

        # Try ActionChains click first
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
            self.human_delay(0.5, 1.2)

            actions = ActionChains(self.driver)
            actions.move_to_element(target).pause(random.uniform(0.2, 0.5)).click().perform()

            logger.info(f"✅ Clicked Select. formGroupId value={target.get_attribute('value')}")
            self.human_delay(2, 4)
            return True
        except Exception as e:
            logger.warning(f"ActionChains click failed: {e}")

        # Fallback: JS click
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
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )

                original_window = self.driver.current_window_handle

                actions = ActionChains(self.driver)
                actions.key_down(Keys.COMMAND if os.name == 'posix' else Keys.CONTROL)
                actions.click(element)
                actions.key_up(Keys.COMMAND if os.name == 'posix' else Keys.CONTROL)
                actions.perform()

                self.human_delay(2, 3)
                WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))

                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        break

                logger.info("Successfully opened Continue link in new tab")
                self.wait_for_page_load()
                return True

            except Exception as e:
                logger.warning(f"Could not open in new tab: {e}")

        for selector in continue_selectors:
            if self.safe_click(selector):
                logger.info("Successfully clicked Continue button (normal click)")
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

        self.take_screenshot("appointment_availability_check.png")

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
                    return True
            except Exception:
                continue

        logger.info("Appointment slots appear to be available")
        print("Yes time")
        return True

    # -----------------------------
    # Master sequence
    # -----------------------------

    def execute_all_steps(self):
        """Execute all steps in sequence."""
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

        # CAPTCHA first (if it appears), then Login submit
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
        if not self.step11_check_appointment_availability():
            return False

        logger.info("🎉 All automation steps completed successfully!")
        return True
