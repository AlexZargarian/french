import time
import logging
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

logger = logging.getLogger(__name__)


class TLSContactSteps:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def remove_url_bar_focus(self):
        """Remove focus from URL bar to eliminate vertical bar in address bar"""
        try:
            # Click on page body to remove focus from URL bar
            self.driver.execute_script("""
                if (document.body) {
                    document.body.focus();
                    document.body.click();
                }
            """)
            # Also try to focus on the first input field or any element on the page
            self.driver.execute_script("""
                var firstInput = document.querySelector('input, button, div, body');
                if (firstInput) {
                    firstInput.focus();
                    firstInput.blur();
                }
            """)
            self.human_delay(0.5, 1)
            logger.debug("✅ URL bar focus removed")
            return True
        except Exception as e:
            logger.warning(f"Could not remove URL bar focus: {e}")
            return False

    def clear_email_field_focus(self, selector, by=By.CSS_SELECTOR):
        """Clear any vertical bar/cursor from email field"""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )

            # Multiple strategies to clear field focus
            self.driver.execute_script("""
                arguments[0].blur();
                arguments[0].value = '';
            """, element)

            # Click away and then back to the element
            body = self.driver.find_element(By.TAG_NAME, 'body')
            body.click()
            self.human_delay(0.3, 0.6)

            element.click()
            self.human_delay(0.3, 0.6)

            # Clear using keyboard
            element.send_keys(Keys.COMMAND + "a" if os.name == 'posix' else Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            self.human_delay(0.2, 0.4)

            logger.debug("✅ Email field focus cleared")
            return True
        except Exception as e:
            logger.warning(f"Could not clear email field focus: {e}")
            return False

    def human_delay(self, min_sec=1, max_sec=3):
        """Add human-like random delays"""
        time.sleep(random.uniform(min_sec, max_sec))

    def ensure_page_focus(self):
        """Ensure focus is on the page, not the URL bar"""
        try:
            # Enhanced focus removal
            self.remove_url_bar_focus()

            # Additional focus on page content
            self.driver.execute_script("""
                if (document.body) {
                    document.body.focus();
                    document.body.click();
                    // Try to focus on any visible element
                    var visibleElement = document.querySelector('input, button, a, div[tabindex]');
                    if (visibleElement && visibleElement.offsetParent !== null) {
                        visibleElement.focus();
                        visibleElement.blur();
                    }
                }
            """)
            self.human_delay(0.3, 0.6)
            logger.debug("✅ Page focus ensured")
            return True
        except Exception as e:
            logger.warning(f"Could not ensure page focus: {e}")
            return False

    def safe_click(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Safely click an element with waiting and retry"""
        try:
            # Ensure focus is on page first and remove URL bar focus
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            # Human-like movement before click
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.2, 0.5))
            actions.click()
            actions.perform()

            self.human_delay(0.5, 1.5)
            return True
        except Exception as e:
            logger.warning(f"Could not click {selector}: {e}")
            return False

    def safe_click_by_xpath(self, xpath, timeout=10):
        """Safely click an element using XPath"""
        try:
            # Ensure focus is on page first
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.2, 0.5))
            actions.click()
            actions.perform()

            self.human_delay(0.5, 1.5)
            return True
        except Exception as e:
            logger.warning(f"Could not click XPath {xpath}: {e}")
            return False

    def safe_type(self, selector, text, by=By.CSS_SELECTOR, timeout=10):
        """Safely type text into an input field - prevent autofill"""
        try:
            # Ensure focus is on page first
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )

            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            # Clear any existing values and set autocomplete off
            self.driver.execute_script("""
                arguments[0].setAttribute('autocomplete', 'off');
                arguments[0].setAttribute('autocorrect', 'off');
                arguments[0].setAttribute('autocapitalize', 'off');
                arguments[0].setAttribute('spellcheck', 'false');
                arguments[0].value = '';
            """, element)

            # Click the field first like a human would
            element.click()
            self.human_delay(0.3, 0.7)

            # Clear using keyboard shortcuts (more human-like)
            element.send_keys(Keys.COMMAND + "a" if os.name == 'posix' else Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            self.human_delay(0.2, 0.5)

            # Type character by character like a human
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.03, 0.1))

            self.human_delay(0.5, 1)
            return True
        except Exception as e:
            logger.warning(f"Could not type in {selector}: {e}")
            return False

    def safe_type_email(self, selector, text, by=By.CSS_SELECTOR, timeout=10):
        """Safely type email with vertical bar focus clearing"""
        try:
            # Ensure focus is on page first
            self.remove_url_bar_focus()
            self.ensure_page_focus()

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )

            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(0.3, 0.6)

            # Clear any existing values and set autocomplete off
            self.driver.execute_script("""
                arguments[0].setAttribute('autocomplete', 'off');
                arguments[0].setAttribute('autocorrect', 'off');
                arguments[0].setAttribute('autocapitalize', 'off');
                arguments[0].setAttribute('spellcheck', 'false');
                arguments[0].value = '';
            """, element)

            # Clear field focus first
            self.driver.execute_script("arguments[0].blur();", element)
            self.human_delay(0.2, 0.4)

            # Click the field first like a human would
            element.click()
            self.human_delay(0.3, 0.7)

            # Clear using keyboard shortcuts (more human-like)
            element.send_keys(Keys.COMMAND + "a" if os.name == 'posix' else Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            self.human_delay(0.2, 0.5)

            # Type character by character like a human
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.03, 0.1))

            self.human_delay(0.5, 1)

            # Blur the field after typing to remove cursor
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
            self.human_delay(2, 4)
            # Ensure focus after page load
            self.remove_url_bar_focus()
            self.ensure_page_focus()
            return True
        except:
            logger.warning("Page load timeout")
            return False

    def wait_for_url_contains(self, url_part, timeout=30):
        """Wait until current URL contains specific text"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.url_contains(url_part)
            )
            logger.info(f"✅ Successfully reached page containing: {url_part}")
            self.wait_for_page_load()
            return True
        except TimeoutException:
            logger.error(f"❌ Timeout waiting for URL to contain: {url_part}")
            return False

    def wait_until_app_domain(self, prefix="https://visas-fr.tlscontact.com/en-us/", timeout=60):
        """
        Wait until we're redirected back to the TLS app domain after login.
        """
        try:
            def on_app_prefix(driver):
                url = driver.current_url or ""
                if "auth/realms" in url:
                    return False
                return url.startswith(prefix)

            WebDriverWait(self.driver, timeout).until(on_app_prefix)
            logger.info(f"✅ Returned to app domain. URL: {self.driver.current_url}")

            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//*[contains(., 'Select') or contains(@href,'workflow') or contains(@href,'service-level')]"
                    ))
                )
                logger.info("✅ Post-login page marker detected (list/workflow link).")
            except TimeoutException:
                logger.warning("⚠️ Post-login marker not detected yet; proceeding anyway.")

            self.wait_for_page_load()
            return True
        except TimeoutException:
            logger.error(
                f"❌ Did not reach app domain with prefix: {prefix} within {timeout}s. Current URL: {self.driver.current_url}")
            return False

    def take_screenshot(self, filename):
        """Take screenshot of current state and delete existing one"""
        try:
            # Delete existing screenshot if it exists
            if os.path.exists(filename):
                os.remove(filename)
                logger.info(f"🗑️  Deleted existing screenshot: {filename}")
        except Exception as e:
            logger.warning(f"Could not delete existing screenshot: {e}")

        # Take new screenshot
        self.driver.save_screenshot(filename)
        logger.info(f"📸 Screenshot saved: {filename}")

    def check_if_already_on_target_page(self):
        """Check if we're already on the service level page"""
        current_url = self.driver.current_url
        if "workflow/service-level" in current_url or "23012573/workflow" in current_url:
            logger.info("✅ Already on target service level page")
            return True
        return False

    def step1_click_book_appointment(self):
        """Step 1: Click the 'Book an appointment' button"""
        logger.info("Step 1: Clicking 'Book an appointment' button...")

        # Ensure page focus before starting
        self.remove_url_bar_focus()
        self.ensure_page_focus()
        self.human_delay(1, 2)

        book_appointment_selectors = [
            "button.TlsButton_tls-button__syUS5.TlsButton_--filled__1vb1H.TlsButton_primary__sPypD.TlsButton_--lg__ElLNd",
        ]

        for selector in book_appointment_selectors:
            if self.safe_click(selector):
                logger.info("✅ Successfully clicked 'Book an appointment'")
                self.wait_for_page_load()
                return True

        xpaths = [
            "//button[contains(@class, 'TlsButton_tls-button__syUS5') and contains(text(), 'Book an appointment')]",
            "//button[contains(., 'Book an appointment')]",
        ]

        for xpath in xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("✅ Successfully clicked 'Book an appointment' (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("❌ Could not find 'Book an appointment' button")
        return False

    def step2_click_france_visas_yes(self):
        """Step 2: Click 'Yes' for 'Have you completed a France-Visas application?'"""
        logger.info("Step 2: Clicking 'Yes' for France-Visas question...")

        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        france_visas_yes_selectors = [
            "button#btn-yes",
            "#btn-yes",
        ]

        for selector in france_visas_yes_selectors:
            if self.safe_click(selector):
                logger.info("✅ Successfully clicked 'Yes' for France-Visas question")
                self.wait_for_page_load()
                return True

        france_visas_xpaths = [
            "//button[@id='btn-yes' and preceding::*[contains(text(), 'France-Visas')]]",
            "//button[@id='btn-yes']"
        ]

        for xpath in france_visas_xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("✅ Successfully clicked 'Yes' for France-Visas question (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("❌ Could not find France-Visas 'Yes' button")
        return False

    def step3_click_tlscontact_yes(self):
        """Step 3: Click 'Yes' for 'Have you registered with TLScontact?'"""
        logger.info("Step 3: Clicking 'Yes' for TLScontact registration question...")

        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "button#btn-yes")
            if len(elements) >= 2:
                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elements[1])
                self.human_delay(0.3, 0.6)

                actions = ActionChains(self.driver)
                actions.move_to_element(elements[1])
                actions.pause(0.3)
                actions.click()
                actions.perform()

                logger.info("✅ Successfully clicked second 'Yes' button")
                self.wait_for_page_load()
                return True
        except:
            pass

        tlscontact_xpaths = [
            "(//button[@id='btn-yes'])[2]",
            "//button[@id='btn-yes' and preceding::*[contains(text(), 'TLScontact')]]",
        ]

        for xpath in tlscontact_xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("✅ Successfully clicked 'Yes' for TLScontact question (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("❌ Could not find TLScontact 'Yes' button")
        return False

    def step4_click_login_button(self):
        """Step 4: Click the 'LOG IN' button"""
        logger.info("Step 4: Clicking 'LOG IN' button...")

        self.human_delay(2, 4)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        login_selectors = [
            "span#btn-select-country",
            "#btn-select-country",
        ]

        for selector in login_selectors:
            if self.safe_click(selector):
                logger.info("✅ Successfully clicked 'LOG IN' button")
                self.wait_for_page_load()
                return True

        login_xpaths = [
            "//span[@id='btn-select-country']",
            "//span[contains(@class, 'TlsButton_tls-button__syUS5') and contains(text(), 'LOG IN')]",
        ]

        for xpath in login_xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("✅ Successfully clicked 'LOG IN' button (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("❌ Could not find 'LOG IN' button")
        return False

    def step5_enter_email(self):
        """Step 5: Enter email in the email input field - with vertical bar fix"""
        logger.info("Step 5: Entering email address...")

        self.human_delay(2, 4)

        # First remove URL bar focus
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        email = os.getenv("TLS_EMAIL", "simonyangor026@gmail.com")

        email_selectors = [
            "input#email-input-field",
            "#email-input-field",
            "input[name='username']",
            "input[type='text'][name='username']",
            "input.tls-input[name='username']"
        ]

        for selector in email_selectors:
            try:
                # First clear any existing focus/vertical bar from the field
                self.clear_email_field_focus(selector)

                # Now type the email using the special email typing method
                if self.safe_type_email(selector, email):
                    logger.info(f"✅ Successfully entered email: {email}")
                    return True
            except Exception as e:
                logger.warning(f"Email selector {selector} failed: {e}")
                continue

        email_xpaths = [
            "//input[@id='email-input-field']",
            "//input[@name='username']",
            "//input[@type='text' and contains(@placeholder, 'email address')]"
        ]

        for xpath in email_xpaths:
            try:
                # Clear focus for XPath elements too
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].blur(); arguments[0].value = '';", element)

                if self.safe_type_email(xpath, email, By.XPATH):
                    logger.info(f"✅ Successfully entered email (XPath): {email}")
                    return True
            except Exception as e:
                logger.warning(f"Email XPath {xpath} failed: {e}")
                continue

        logger.error("❌ Could not find email input field")
        return False

    def step6_enter_password(self):
        """Step 6: Enter password in the password input field"""
        logger.info("Step 6: Entering password...")

        self.remove_url_bar_focus()
        self.ensure_page_focus()

        password = os.getenv("TLS_PASSWORD", "Dilijan24$")

        password_selectors = [
            "input#password-input-field",
            "#password-input-field",
            "input[name='password']",
            "input[type='password']",
            "input.tls-input[name='password']"
        ]

        for selector in password_selectors:
            if self.safe_type(selector, password):
                logger.info("✅ Successfully entered password")
                return True

        password_xpaths = [
            "//input[@id='password-input-field']",
            "//input[@name='password']",
            "//input[@type='password']"
        ]

        for xpath in password_xpaths:
            if self.safe_type(xpath, password, By.XPATH):
                logger.info("✅ Successfully entered password (XPath)")
                return True

        logger.error("❌ Could not find password input field")
        return False

    def step7_click_login_submit(self):
        """Step 7: Click the final Login submit button"""
        logger.info("Step 7: Clicking Login submit button...")

        self.remove_url_bar_focus()
        self.ensure_page_focus()
        self.human_delay(1, 2)

        login_submit_selectors = [
            "button#btn-login",
            "#btn-login",
            "button.bg-primary-500"
        ]

        for selector in login_submit_selectors:
            if self.safe_click(selector):
                logger.info("✅ Successfully clicked Login submit button")
                self.wait_for_page_load()
                return True

        login_submit_xpaths = [
            "//button[@id='btn-login']",
            "//button[contains(@class, 'bg-primary-500') and contains(text(), 'Login')]",
            "//button[normalize-space()='Login']"
        ]

        for xpath in login_submit_xpaths:
            if self.safe_click_by_xpath(xpath):
                logger.info("✅ Successfully clicked Login submit button (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("❌ Could not find Login submit button")
        return False

    def step8_click_select_button(self):
        """Step 8: Click the Select button with value 23012573"""
        logger.info("Step 8: Clicking Select button...")

        self.human_delay(5, 8)
        self.wait_for_page_load(timeout=30)
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        logger.info("🔄 Strategy 1: Trying alternative selectors...")
        alternative_selectors = [
            "button[value='23012573']",
            "button[name='formGroupId'][value='23012573']",
            "button.TlsButton_tls-button__syUS5[value='23012573']",
            "button.flex-1[value='23012573']",
        ]

        for selector in alternative_selectors:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                self.human_delay(1, 2)
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"✅ Successfully clicked using selector: {selector}")
                self.human_delay(2, 4)
                return True
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {e}")

        logger.info("🔄 Strategy 2: Waiting for button to be clickable...")
        try:
            button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[value='23012573']"))
            )

            button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[value='23012573']"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            self.human_delay(1, 2)

            self.driver.execute_script("arguments[0].click();", button)
            logger.info("✅ Successfully clicked Select button using JavaScript after explicit wait")
            self.human_delay(2, 4)
            return True
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}")

        logger.info("🔄 Strategy 3: Trying XPaths...")
        xpaths = [
            "//button[@value='23012573']",
            "//button[@value='23012573' and text()='Select']",
            "//button[@name='formGroupId' and @value='23012573']",
        ]

        for xpath in xpaths:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                self.human_delay(1, 2)
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"✅ Successfully clicked using XPath: {xpath}")
                self.human_delay(2, 4)
                return True
            except Exception as e:
                logger.warning(f"XPath {xpath} failed: {e}")

        if self.check_if_already_on_target_page():
            logger.info("✅ Already on service level page - no need to click Select button")
            return True

        logger.error("❌ All strategies failed to click Select button")
        return False

    def step9_wait_for_service_level_page(self):
        """Step 9: Wait for service level page to load"""
        logger.info("Step 9: Waiting for service level page to load...")

        target_url_parts = ["workflow/service-level", "23012573/workflow"]

        for url_part in target_url_parts:
            if self.wait_for_url_contains(url_part, timeout=30):
                logger.info(f"✅ Successfully reached service level page (matched: {url_part})")
                return True

        if self.check_if_already_on_target_page():
            logger.info("✅ Already on service level page")
            return True

        logger.error("❌ Failed to reach service level page")
        return False

    def step10_click_continue_button(self):
        """Step 10: Click Continue button to open appointment booking"""
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

                logger.info("✅ Successfully opened Continue link in new tab")
                self.wait_for_page_load()
                return True

            except Exception as e:
                logger.warning(f"Could not open in new tab: {e}")
                continue

        for selector in continue_selectors:
            if self.safe_click(selector):
                logger.info("✅ Successfully clicked Continue button (normal click)")
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
                logger.info("✅ Successfully clicked Continue button (XPath)")
                self.wait_for_page_load()
                return True

        logger.error("❌ Could not find Continue button")
        return False

    def step11_check_appointment_availability(self):
        """Step 11: Check if appointment slots are available"""
        logger.info("Step 11: Checking appointment availability...")

        self.human_delay(3, 5)
        self.wait_for_page_load()
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        # Take only this screenshot and delete existing one
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
                    logger.info("❌ No appointment slots available message detected")
                    print("No time")
                    return True
            except:
                continue

        logger.info("✅ Appointment slots appear to be available")
        print("Yes time")
        return True

    def execute_all_steps(self):
        """Execute all 11 steps in sequence"""
        logger.info("Starting TLSContact automation sequence...")

        steps = [
            ("Book Appointment", self.step1_click_book_appointment),
            ("France-Visas Yes", self.step2_click_france_visas_yes),
            ("TLScontact Yes", self.step3_click_tlscontact_yes),
            ("LOG IN", self.step4_click_login_button),
            ("Enter Email", self.step5_enter_email),
            ("Enter Password", self.step6_enter_password),
            ("Login Submit", self.step7_click_login_submit),
            ("Wait After Login (app domain)", lambda: self.wait_until_app_domain(
                prefix="https://visas-fr.tlscontact.com/en-us/", timeout=60
            )),
            ("Select Button", self.step8_click_select_button),
            ("Wait Service Level", self.step9_wait_for_service_level_page),
            ("Continue Button", self.step10_click_continue_button),
            ("Check Availability", self.step11_check_appointment_availability),
        ]

        for step_name, step_function in steps:
            logger.info(f"--- Executing: {step_name} ---")

            if step_name == "Select Button" and self.check_if_already_on_target_page():
                logger.info("⏭️  Skipping Select Button - already on target page")
                continue

            if not step_function():
                logger.error(f"❌ Failed at step: {step_name}")
                return False
            self.human_delay(2, 4)

        logger.info("🎉 All 11 steps completed successfully!")
        return True