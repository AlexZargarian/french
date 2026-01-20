import time
import logging
import random
import os
import json
from datetime import datetime

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

        # Initialize failure tracking
        self.failure_log_file = "failure_log.json"
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.load_failure_count()
        self.last_failed_step = None

    # -----------------------------
    # NEW: Ultra-Human-like CAPTCHA Clicking Methods
    # -----------------------------

    def simulate_reading_captcha(self):
        """Simulate reading the CAPTCHA text like a human"""
        logger.info("Reading CAPTCHA text like a human...")

        # Humans don't instantly react - they read first
        reading_time = random.uniform(1.5, 3.5)
        logger.info(f"Pausing {reading_time:.1f} seconds as if reading CAPTCHA")
        time.sleep(reading_time)

        # Sometimes humans glance away and back
        if random.random() < 0.3:  # 30% chance
            glance_time = random.uniform(0.5, 1.2)
            logger.info(f"Glancing away for {glance_time:.1f} seconds")
            time.sleep(glance_time)

    def create_human_mouse_path(self, element, start_x=None, start_y=None):
        """Create a human-like mouse movement path to the element"""
        try:
            # Get element location and size
            location = element.location_once_scrolled_into_view
            size = element.size

            # Target within the element (not perfect center)
            target_x = location['x'] + random.randint(
                int(size['width'] * 0.3),
                int(size['width'] * 0.7)
            )
            target_y = location['y'] + random.randint(
                int(size['height'] * 0.3),
                int(size['height'] * 0.7)
            )

            # If no start position provided, start near current position
            if start_x is None or start_y is None:
                start_x = random.randint(100, 300)
                start_y = random.randint(100, 300)

            actions = ActionChains(self.driver)

            # Start from current position
            actions.move_by_offset(start_x, start_y)

            # Create natural path with 2-3 intermediate points
            num_points = random.randint(2, 3)

            for i in range(num_points):
                # Calculate point along the path with slight curve
                progress = (i + 1) / (num_points + 1)

                # Add natural curve (bezier-like)
                curve_offset_x = random.randint(-25, 25)
                curve_offset_y = random.randint(-15, 15)

                inter_x = start_x + (target_x - start_x) * progress + curve_offset_x
                inter_y = start_y + (target_y - start_y) * progress + curve_offset_y

                # Calculate distance for speed variation
                distance_x = inter_x - (start_x if i == 0 else prev_x)
                distance_y = inter_y - (start_y if i == 0 else prev_y)
                distance = (distance_x**2 + distance_y**2)**0.5

                # Vary speed - faster for longer distances, slower for short
                speed_factor = 0.1 + (distance / 500) * 0.3
                duration = random.uniform(0.08, 0.15) * speed_factor

                actions.move_by_offset(distance_x, distance_y)
                actions.pause(duration)

                # Sometimes pause briefly during movement (like human hesitation)
                if random.random() < 0.2:
                    actions.pause(random.uniform(0.05, 0.1))

                prev_x, prev_y = inter_x, inter_y

            # Final movement to target
            final_x = target_x - prev_x
            final_y = target_y - prev_y
            final_distance = (final_x**2 + final_y**2)**0.5
            final_duration = random.uniform(0.05, 0.1) * (1 + final_distance / 300)

            actions.move_by_offset(final_x, final_y)
            actions.pause(final_duration)

            # Slight overshoot then correction (very human-like)
            if random.random() < 0.4:  # 40% chance
                overshoot_x = random.randint(-5, 5)
                overshoot_y = random.randint(-3, 3)
                actions.move_by_offset(overshoot_x, overshoot_y)
                actions.pause(0.02)
                actions.move_by_offset(-overshoot_x, -overshoot_y)
                actions.pause(0.02)

            actions.perform()

            # Small pause at target (like aiming)
            time.sleep(random.uniform(0.05, 0.12))

            return target_x, target_y

        except Exception as e:
            logger.warning(f"Human mouse path creation failed: {e}")
            # Fallback: just move to element
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            time.sleep(random.uniform(0.1, 0.2))
            return None, None

    def human_click_with_variation(self, element):
        """Click with human-like variations in timing and pressure"""
        try:
            actions = ActionChains(self.driver)

            # 1. Pre-click hesitation (humans don't click instantly)
            hesitation = random.uniform(0.1, 0.25)
            actions.pause(hesitation)

            # 2. Press down with variable timing
            press_duration = random.uniform(0.03, 0.08)

            # 3. Sometimes click quickly, sometimes more deliberately
            if random.random() < 0.7:  # 70%: normal click
                actions.click_and_hold(element)
                actions.pause(press_duration)
                actions.release(element)
            else:  # 30%: more deliberate click (slightly longer)
                actions.click_and_hold(element)
                actions.pause(press_duration * 1.5)  # Longer hold
                actions.release(element)

            actions.perform()

            # 4. Post-click reaction time
            reaction_time = random.uniform(0.05, 0.15)
            time.sleep(reaction_time)

            # 5. Sometimes move mouse away after clicking
            if random.random() < 0.6:  # 60% chance
                move_away_x = random.randint(-20, 20)
                move_away_y = random.randint(-10, 10)
                actions = ActionChains(self.driver)
                actions.move_by_offset(move_away_x, move_away_y)
                actions.perform()
                time.sleep(random.uniform(0.05, 0.1))

            logger.info("✅ Human-like click performed")

        except Exception as e:
            logger.warning(f"Human click failed: {e}")
            # Fallback
            element.click()

    def simulate_human_decision_making(self):
        """Simulate the human decision-making process before clicking CAPTCHA"""
        # Humans don't just click - they think about it
        logger.info("Simulating human decision-making...")

        # Random decision process timing
        decision_phases = random.randint(1, 3)

        for phase in range(decision_phases):
            # Small pauses while "thinking"
            think_time = random.uniform(0.3, 0.8)
            time.sleep(think_time)

            # Sometimes move mouse slightly while thinking
            if random.random() < 0.4:
                actions = ActionChains(self.driver)
                actions.move_by_offset(
                    random.randint(-15, 15),
                    random.randint(-10, 10)
                ).pause(0.1).perform()

        # Final decision pause
        final_pause = random.uniform(0.2, 0.5)
        time.sleep(final_pause)

    def handle_captcha_ultra_human(self):
        """
        Ultra-human-like CAPTCHA handling that mimics exactly how a human would do it
        """
        logger.info("🤔 Starting ultra-human-like CAPTCHA handling...")

        try:
            # Wait a natural amount of time before even looking for CAPTCHA
            time.sleep(random.uniform(2.0, 3.5))

            # Look for CAPTCHA iframes naturally
            iframe_selectors = [
                "iframe[title*='recaptcha']",
                "iframe[src*='recaptcha']",
                "iframe[title*='challenge']",
                "iframe[title*='I'm not a robot']",
                "iframe[title*='checkbox']"
            ]

            captcha_found = False
            for selector in iframe_selectors:
                try:
                    iframes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for iframe in iframes:
                        if iframe.is_displayed():
                            logger.info(f"Found CAPTCHA iframe: {selector}")
                            captcha_found = True

                            # Switch to iframe
                            self.driver.switch_to.frame(iframe)

                            # Human-like behavior: look at CAPTCHA
                            self.simulate_reading_captcha()

                            # Try different checkbox selectors
                            checkbox_selectors = [
                                ".recaptcha-checkbox-border",
                                ".recaptcha-checkbox",
                                "div[role='checkbox']",
                                "#recaptcha-anchor",
                                "span.recaptcha-checkbox"
                            ]

                            checkbox = None
                            for cb_selector in checkbox_selectors:
                                try:
                                    checkbox = self.driver.find_element(By.CSS_SELECTOR, cb_selector)
                                    if checkbox.is_displayed():
                                        logger.info(f"Found CAPTCHA checkbox: {cb_selector}")
                                        break
                                except:
                                    continue

                            if checkbox:
                                # Scroll to make it visible (like a human would)
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                                time.sleep(random.uniform(0.3, 0.7))

                                # Simulate decision-making process
                                self.simulate_human_decision_making()

                                # Move to checkbox with ultra-human-like path
                                logger.info("Moving to CAPTCHA checkbox like a human...")
                                self.create_human_mouse_path(checkbox)

                                # Final hesitation before click
                                time.sleep(random.uniform(0.1, 0.3))

                                # Perform ultra-human-like click
                                logger.info("Clicking CAPTCHA checkbox with human-like variations...")
                                self.human_click_with_variation(checkbox)

                                # Switch back to main content
                                self.driver.switch_to.default_content()

                                # Natural waiting for response
                                wait_time = random.uniform(2.5, 4.5)
                                logger.info(f"Waiting {wait_time:.1f}s for CAPTCHA response (natural human wait)")
                                time.sleep(wait_time)

                                # Check if image challenge appeared
                                if self.check_for_image_challenge():
                                    logger.warning("⚠️ Image selection challenge appeared")
                                    # Don't try to solve it, just report
                                    self.driver.switch_to.default_content()
                                    return False
                                else:
                                    logger.info("✅ CAPTCHA clicked successfully with ultra-human-like behavior")
                                    return True

                            # Switch back if checkbox not found
                            self.driver.switch_to.default_content()

                except Exception as e:
                    logger.debug(f"Trying selector {selector}: {e}")
                    continue

            if not captcha_found:
                logger.info("ℹ️ No CAPTCHA iframe found")

            return False

        except Exception as e:
            logger.warning(f"Ultra-human CAPTCHA handling error: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    # -----------------------------
    # Failure tracking methods
    # -----------------------------

    def load_failure_count(self):
        """Load consecutive failure count from file"""
        try:
            if os.path.exists(self.failure_log_file):
                with open(self.failure_log_file, 'r') as f:
                    data = json.load(f)
                    self.consecutive_failures = data.get('consecutive_failures', 0)
                    self.last_failed_step = data.get('last_failed_step', None)
                    logger.info(f"Loaded failure count: {self.consecutive_failures}")
                    if self.last_failed_step:
                        logger.info(f"Last failed at step: {self.last_failed_step}")
            else:
                self.consecutive_failures = 0
                self.last_failed_step = None
        except Exception as e:
            logger.warning(f"Could not load failure count: {e}")
            self.consecutive_failures = 0
            self.last_failed_step = None

    def save_failure_count(self):
        """Save consecutive failure count to file"""
        try:
            data = {
                'consecutive_failures': self.consecutive_failures,
                'last_failed_step': self.last_failed_step,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.failure_log_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Could not save failure count: {e}")

    def record_success(self):
        """Reset failure count on successful completion"""
        if self.consecutive_failures > 0:
            logger.info(f"✅ Resetting failure count from {self.consecutive_failures} to 0")
            self.consecutive_failures = 0
            self.last_failed_step = None
            self.save_failure_count()

    def record_failure(self, step_name=None):
        """Increment failure count and check if alert needed"""
        self.consecutive_failures += 1
        if step_name:
            self.last_failed_step = step_name

        logger.warning(f"❌ Failure #{self.consecutive_failures} recorded")
        if step_name:
            logger.warning(f"Failed at step: {step_name}")

        self.save_failure_count()

        # Check if we need to send alert
        if self.consecutive_failures >= self.max_consecutive_failures:
            self.send_error_alert()

    # -----------------------------
    # Error Telegram helper (separate from regular bot)
    # -----------------------------

    def telegram_send_error_message(self, text: str) -> bool:
        """Send message using error-specific Telegram bot"""
        token = os.getenv("TELEGRAM_ERROR_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_ERROR_CHAT_ID")

        if not token or not chat_id:
            logger.warning("Error Telegram env vars missing: TELEGRAM_ERROR_BOT_TOKEN / TELEGRAM_ERROR_CHAT_ID")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            r = requests.post(url, data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }, timeout=15)
            if r.status_code != 200:
                logger.warning(f"Error Telegram sendMessage failed: {r.status_code} {r.text}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Error Telegram sendMessage error: {e}")
            return False

    def telegram_send_error_photo(self, photo_path: str, caption: str = "") -> bool:
        """Send photo using error-specific Telegram bot"""
        token = os.getenv("TELEGRAM_ERROR_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_ERROR_CHAT_ID")

        if not token or not chat_id:
            logger.warning("Error Telegram env vars missing: TELEGRAM_ERROR_BOT_TOKEN / TELEGRAM_ERROR_CHAT_ID")
            return False

        if not os.path.exists(photo_path):
            logger.warning(f"Screenshot not found: {photo_path}")
            return False

        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        try:
            with open(photo_path, "rb") as f:
                files = {"photo": f}
                data = {
                    "chat_id": chat_id,
                    "caption": caption[:1024] if caption else "",  # Telegram caption limit
                    "parse_mode": "HTML"
                }
                r = requests.post(url, data=data, files=files, timeout=60)

            if r.status_code != 200:
                logger.warning(f"Error Telegram sendPhoto failed: {r.status_code} {r.text}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Error Telegram sendPhoto error: {e}")
            return False

    # -----------------------------
    # Error alert method (UPDATED to use error bot)
    # -----------------------------

    def send_error_alert(self):
        """Send error alert with screenshot using error-specific bot"""
        logger.warning(f"🚨 SENDING ERROR ALERT: {self.consecutive_failures} consecutive failures")

        # Get current time and URL for context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_url = self.driver.current_url if hasattr(self.driver, 'current_url') else "Unknown"
        page_title = self.driver.title if hasattr(self.driver, 'title') else "Unknown"

        # Create detailed error message
        error_message = (
            f"<b>🚨 TLSContact Automation Failed</b>\n\n"
            f"<b>Consecutive Failures:</b> {self.consecutive_failures}\n"
            f"<b>Time:</b> {current_time}\n"
        )

        if self.last_failed_step:
            error_message += f"<b>Failed Step:</b> {self.last_failed_step}\n"

        error_message += f"<b>URL:</b> {current_url[:200] if current_url else 'N/A'}\n"
        error_message += f"<b>Page Title:</b> {page_title[:100] if page_title else 'N/A'}\n\n"
        error_message += "⚠️ <b>Manual intervention required!</b>"

        # Send error message via error bot
        success = self.telegram_send_error_message(error_message)

        if not success:
            logger.error("Failed to send error message via error Telegram bot")
            # Fallback to regular bot
            logger.info("Trying fallback to regular Telegram bot...")
            return self.telegram_send_message(f"⚠️ Error bot failed! {error_message}")

        # Take and send screenshot
        try:
            screenshot_filename = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.take_screenshot(screenshot_filename)

            # Create screenshot caption
            caption = (
                f"<b>Failure Screenshot</b>\n"
                f"Step: {self.last_failed_step or 'Unknown'}\n"
                f"Time: {current_time}"
            )

            # Send screenshot via error bot
            photo_sent = self.telegram_send_error_photo(screenshot_filename, caption=caption)

            if not photo_sent:
                logger.error("Failed to send screenshot via error Telegram bot")
                # Fallback to regular bot
                self.telegram_send_photo(screenshot_filename,
                                         caption=f"Error bot failed! Step: {self.last_failed_step or 'Unknown'}")

            # Clean up screenshot after sending
            try:
                if os.path.exists(screenshot_filename):
                    os.remove(screenshot_filename)
                    logger.info(f"Cleaned up screenshot: {screenshot_filename}")
            except Exception as e:
                logger.warning(f"Could not delete screenshot: {e}")

            logger.info(f"✅ Error alert sent with screenshot: {screenshot_filename}")

        except Exception as e:
            logger.error(f"Failed to send error screenshot: {e}")
            # Still send a text message about the error
            self.telegram_send_error_message(f"⚠️ Screenshot failed: {str(e)[:100]}")

    # -----------------------------
    # Telegram helpers (regular bot for availability notifications)
    # -----------------------------

    def telegram_send_message(self, text: str) -> bool:
        """Send message using regular Telegram bot (for availability notifications)"""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            logger.warning("Regular Telegram env vars missing: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            r = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=15)
            if r.status_code != 200:
                logger.warning(f"Regular Telegram sendMessage failed: {r.status_code} {r.text}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Regular Telegram sendMessage error: {e}")
            return False

    def telegram_send_photo(self, photo_path: str, caption: str = "") -> bool:
        """Send photo using regular Telegram bot (for availability notifications)"""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            logger.warning("Regular Telegram env vars missing: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
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
                logger.warning(f"Regular Telegram sendPhoto failed: {r.status_code} {r.text}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Regular Telegram sendPhoto error: {e}")
            return False

    # -----------------------------
    # Enhanced Human-like Behavior Methods
    # -----------------------------

    def simulate_human_pre_login_behavior(self):
        """Simulate natural human behavior on the login page BEFORE entering credentials"""
        logger.info("🎭 Simulating human pre-login behavior...")

        try:
            # 1. Wait naturally for page to load
            time.sleep(random.uniform(3.0, 5.0))

            # 2. Natural scrolling to explore the page
            scroll_patterns = [
                (-200, 400),   # Scroll down a bit
                (100, -100),   # Scroll back up a bit
                (-300, 300),   # Scroll down more
            ]

            for scroll_up, scroll_down in scroll_patterns:
                self.driver.execute_script(f"window.scrollBy(0, {scroll_up});")
                time.sleep(random.uniform(0.5, 1.2))
                self.driver.execute_script(f"window.scrollBy(0, {scroll_down});")
                time.sleep(random.uniform(0.3, 0.8))

            # 3. Move mouse naturally around the page
            self.simulate_natural_browsing_mouse_movements()

            # 4. Briefly "read" the page
            self.simulate_reading_page_content()

            # 5. Natural delay before starting to type
            time.sleep(random.uniform(1.5, 3.0))

            logger.info("✅ Completed human pre-login simulation")
            return True

        except Exception as e:
            logger.warning(f"Pre-login simulation error: {e}")
            return True  # Continue anyway

    def simulate_natural_browsing_mouse_movements(self):
        """Simulate how a human actually moves a mouse when browsing"""
        try:
            actions = ActionChains(self.driver)

            # Get page dimensions
            width = self.driver.execute_script("return window.innerWidth")
            height = self.driver.execute_script("return window.innerHeight")

            # Start from a random position
            start_x = random.randint(100, width - 200)
            start_y = random.randint(100, height - 200)

            # Move to starting position
            actions.move_by_offset(start_x, start_y)
            actions.pause(random.uniform(0.2, 0.4))

            # Create natural wandering path
            for i in range(random.randint(5, 10)):
                if i % 3 == 0:
                    # Occasionally make a larger movement
                    offset_x = random.randint(-150, 150)
                    offset_y = random.randint(-100, 100)
                    duration = random.uniform(0.3, 0.6)
                else:
                    # Small, natural adjustments
                    offset_x = random.randint(-30, 30)
                    offset_y = random.randint(-20, 20)
                    duration = random.uniform(0.1, 0.25)

                actions.move_by_offset(offset_x, offset_y)
                actions.pause(duration)

                # Occasionally pause longer (like reading)
                if random.random() < 0.2:
                    actions.pause(random.uniform(0.5, 1.0))

            actions.perform()
            self.human_delay(0.5, 1.0)

        except Exception:
            pass

    def simulate_reading_page_content(self):
        """Simulate reading the page by hovering over text elements"""
        try:
            # Find text elements that a human might read
            text_selectors = [
                "h1", "h2", "h3",
                "label",
                "div[class*='text']",
                "span[class*='label']",
                "p", "div > strong"
            ]

            all_elements = []
            for selector in text_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [e for e in elements if e.is_displayed() and e.size['height'] > 0]
                    all_elements.extend(visible_elements[:3])
                except:
                    continue

            # Randomly select 1-3 elements to "read"
            if all_elements:
                elements_to_read = random.sample(
                    all_elements,
                    min(random.randint(1, 3), len(all_elements))
                )

                for element in elements_to_read:
                    try:
                        # Move to element with slight offset
                        offset_x = random.randint(-10, 10)
                        offset_y = random.randint(-5, 5)

                        actions = ActionChains(self.driver)
                        actions.move_to_element_with_offset(element, offset_x, offset_y)

                        # Pause as if reading
                        text_length = len(element.text) if element.text else 0
                        read_time = min(2.0, max(0.5, text_length / 50))
                        actions.pause(read_time)

                        actions.perform()

                        # Small delay between reading different elements
                        time.sleep(random.uniform(0.2, 0.5))

                    except Exception:
                        continue

        except Exception:
            pass

    def move_to_element_human_like(self, element):
        """Move to element with natural human cursor movement"""
        try:
            # Get element location
            location = element.location_once_scrolled_into_view
            size = element.size

            # Don't move directly to center - humans are imprecise
            target_x = location['x'] + random.randint(
                size['width'] // 3,
                size['width'] * 2 // 3
            )
            target_y = location['y'] + random.randint(
                size['height'] // 3,
                size['height'] * 2 // 3
            )

            # Create natural curved movement path
            actions = ActionChains(self.driver)

            # Start from current position (or random nearby)
            current_x, current_y = 0, 0

            # Add 1-2 intermediate points for natural curve
            intermediate_points = random.randint(1, 2)

            for i in range(intermediate_points):
                # Calculate intermediate point with slight curve
                progress = (i + 1) / (intermediate_points + 1)
                inter_x = current_x + (target_x - current_x) * progress + random.randint(-20, 20)
                inter_y = current_y + (target_y - current_y) * progress + random.randint(-15, 15)

                # Move to intermediate point with variable speed
                move_x = inter_x - current_x
                move_y = inter_y - current_y
                duration = random.uniform(0.1, 0.3) * (1 + abs(move_x + move_y) / 200)

                actions.move_by_offset(move_x, move_y)
                actions.pause(duration)

                current_x, current_y = inter_x, inter_y

            # Final movement to target
            final_x = target_x - current_x
            final_y = target_y - current_y
            actions.move_by_offset(final_x, final_y)
            actions.pause(random.uniform(0.05, 0.15))

            actions.perform()
            time.sleep(random.uniform(0.1, 0.3))

        except Exception:
            # Fallback to simple move
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()

    def click_element_human_like(self, element):
        """Click with human-like timing and precision"""
        try:
            actions = ActionChains(self.driver)

            # Slight hesitation before clicking
            actions.pause(random.uniform(0.05, 0.2))

            # Click with natural press/release timing
            actions.click_and_hold(element)
            actions.pause(random.uniform(0.05, 0.12))
            actions.release(element)

            actions.perform()

            # Natural reaction time after click
            time.sleep(random.uniform(0.1, 0.25))

        except Exception:
            element.click()

    def type_human_like(self, element, text, field_type="text"):
        """Type text with human-like patterns"""
        try:
            # Clear existing text with backspacing like a human
            current_value = element.get_attribute('value') or ''
            if current_value:
                # Move to end of text
                element.send_keys(Keys.END)
                time.sleep(random.uniform(0.1, 0.3))

                # Backspace with variable speed
                for i in range(len(current_value)):
                    element.send_keys(Keys.BACKSPACE)
                    if i < len(current_value) - 3:
                        time.sleep(random.uniform(0.02, 0.06))
                    else:
                        time.sleep(random.uniform(0.04, 0.1))

            # Type the new text with human patterns
            for i, char in enumerate(text):
                # Vary typing speed
                if i == 0:  # First character
                    delay = random.uniform(0.1, 0.2)
                elif i < 3:  # First few characters
                    delay = random.uniform(0.08, 0.15)
                elif i > len(text) - 3:  # Last few characters
                    delay = random.uniform(0.06, 0.12)
                else:  # Middle characters
                    delay = random.uniform(0.03, 0.08)

                # Occasionally "make a mistake" and correct (5% chance)
                if random.random() < 0.05:
                    wrong_char = random.choice(['a', 'e', 'i', 'o', 'u', 's', 't', 'n'])
                    element.send_keys(wrong_char)
                    time.sleep(random.uniform(0.05, 0.15))
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.05, 0.15))

                element.send_keys(char)
                time.sleep(delay)

                # Occasionally pause to "think" (10% chance)
                if random.random() < 0.1:
                    think_time = random.uniform(0.2, 0.6)
                    time.sleep(think_time)

            # Final pause after typing
            if field_type == "password":
                time.sleep(random.uniform(0.3, 0.8))
            else:
                time.sleep(random.uniform(0.2, 0.5))

            return True

        except Exception as e:
            logger.warning(f"Human-like typing failed: {e}")
            return False

    def enter_credentials_human_like(self, email, password):
        """Enter email and password with human-like patterns"""
        logger.info("🔐 Entering credentials with human-like patterns...")

        try:
            # Find email field
            email_selectors = [
                "input#email-input-field",
                "#email-input-field",
                "input[name='username']",
                "input[type='email']",
                "input[autocomplete='email']"
            ]

            email_field = None
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if email_field.is_displayed():
                        break
                    else:
                        email_field = None
                except:
                    continue

            if not email_field:
                logger.error("Email field not found")
                return False

            # Simulate noticing and deciding to type
            time.sleep(random.uniform(1.0, 2.0))

            # Move to email field with hesitation
            self.move_to_element_human_like(email_field)
            time.sleep(random.uniform(0.5, 1.2))

            # Click with imprecision
            self.click_element_human_like(email_field)

            # Type email
            self.type_human_like(email_field, email, field_type="email")

            # Natural transition to password field
            time.sleep(random.uniform(0.8, 1.5))

            # Find password field
            password_selectors = [
                "input#password-input-field",
                "#password-input-field",
                "input[name='password']",
                "input[type='password']"
            ]

            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if password_field.is_displayed():
                        break
                except:
                    continue

            if password_field:
                self.move_to_element_human_like(password_field)
                time.sleep(random.uniform(0.3, 0.8))
                self.click_element_human_like(password_field)
            else:
                # Press Tab as fallback
                email_field.send_keys(Keys.TAB)
                time.sleep(random.uniform(0.5, 1.0))
                password_field = self.driver.switch_to.active_element

            # Type password
            self.type_human_like(password_field, password, field_type="password")

            logger.info("✅ Credentials entered with human-like patterns")
            return True

        except Exception as e:
            logger.error(f"Human-like credential entry failed: {e}")
            return False

    # -----------------------------
    # UPDATED: handle_captcha_subtle now uses ultra-human approach
    # -----------------------------

    def handle_captcha_subtle(self):
        """Use ultra-human-like approach for CAPTCHA"""
        return self.handle_captcha_ultra_human()

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

            # Use human-like typing
            if not self.type_human_like(element, text):
                # Fallback to original method
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

            # Use human-like typing
            if not self.type_human_like(element, text, field_type="email"):
                # Fallback
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

            # Calculate target position
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
                # Wait for CAPTCHA response
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

    def step11_check_appointment_availability(self, month_label="current"):
        """Check appointment availability for a specific month"""
        logger.info(f"Step 11: Checking {month_label} month appointment availability...")
        self.human_delay(3, 5)
        self.wait_for_page_load()
        self.remove_url_bar_focus()
        self.ensure_page_focus()

        # Create unique screenshot filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"appointment_{month_label}_{timestamp}.png"
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
                    logger.info(f"No appointment slots available in {month_label} month")
                    print(f"No time ({month_label} month)")

                    # Send to Telegram with month label
                    self.telegram_send_message(f"❌ No time ({month_label} month)")
                    self.telegram_send_photo(screenshot_path, caption=f"{month_label.capitalize()} month - No time - Screenshot")

                    # Clean up screenshot after sending
                    try:
                        if os.path.exists(screenshot_path):
                            os.remove(screenshot_path)
                    except Exception:
                        pass

                    return True
            except Exception:
                continue

        # If no "no slots" message found
        logger.info(f"Appointment slots appear to be available in {month_label} month")
        print(f"Yes time ({month_label} month)")

        # Send to Telegram with month label
        self.telegram_send_message(f"✅ Yes time ({month_label} month)")
        self.telegram_send_photo(screenshot_path, caption=f"{month_label.capitalize()} month - Yes time - Screenshot")

        # Clean up screenshot after sending
        try:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
        except Exception:
            pass

        return True

    # -----------------------------
    # NEW STEP 12: Click next month button
    # -----------------------------

    def step12_click_next_month(self):
        """
        Step 12: Automatically find and click the next month button
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

            # Get the month text
            month_text = next_month_button.text
            logger.info(f"Found next month button: {month_text}")

            # Click it
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_month_button)
            self.human_delay(0.5, 1)

            # Use human-like click
            self.click_element_human_like(next_month_button)

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

                                # Use human-like click
                                self.click_element_human_like(element)

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
    # Main execution method (UPDATED with ultra-human-like CAPTCHA)
    # -----------------------------

    def execute_all_steps(self):
        logger.info("Starting TLSContact automation sequence...")
        logger.info(f"Current consecutive failures: {self.consecutive_failures}")

        try:
            # Execute initial steps
            if not self.step1_click_book_appointment():
                self.record_failure("Step 1: Book appointment")
                return False

            if not self.step2_click_france_visas_yes():
                self.record_failure("Step 2: France-Visas Yes")
                return False

            if not self.step3_click_tlscontact_yes():
                self.record_failure("Step 3: TLScontact Yes")
                return False

            if not self.step4_click_login_button():
                self.record_failure("Step 4: Login button")
                return False

            # IMPORTANT: Wait for login page to fully load
            self.wait_for_page_load(timeout=15)

            # CRITICAL: Simulate human behavior BEFORE entering credentials
            logger.info("🎭 Simulating natural human behavior on login page...")
            self.simulate_human_pre_login_behavior()

            # Get credentials
            email = os.getenv("TLS_EMAIL", "")
            password = os.getenv("TLS_PASSWORD", "")

            if not email or not password:
                logger.error("Email or password not set in environment variables")
                self.record_failure("Credentials not set")
                return False

            # Enter credentials with human-like patterns
            logger.info("🔐 Entering credentials with human-like patterns...")
            if not self.enter_credentials_human_like(email, password):
                # Fallback to original methods
                logger.info("Falling back to original credential entry...")
                if not self.step5_enter_email():
                    self.record_failure("Step 5: Enter email")
                    return False

                time.sleep(random.uniform(1.0, 2.0))

                if not self.step6_enter_password():
                    self.record_failure("Step 6: Enter password")
                    return False

            # Natural pause before CAPTCHA
            logger.info("⏳ Natural pause before CAPTCHA...")
            time.sleep(random.uniform(2.0, 3.5))

            # USE ULTRA-HUMAN CAPTCHA HANDLING
            logger.info("🎯 Using ultra-human-like CAPTCHA handling...")
            captcha_result = self.handle_captcha_ultra_human()

            if not captcha_result:
                logger.info("ℹ️ No CAPTCHA detected or could not solve")

            # Natural pause before submitting
            time.sleep(random.uniform(1.0, 2.0))

            if not self.step7_click_login_submit():
                self.record_failure("Step 7: Login submit")
                return False

            if not self.wait_until_app_domain(prefix="https://visas-fr.tlscontact.com/en-us/", timeout=60):
                self.record_failure("Step 7b: Wait for app domain")
                return False

            if not self.check_if_already_on_target_page():
                if not self.step8_click_select_button():
                    self.record_failure("Step 8: Select button")
                    return False

            if not self.step9_wait_for_service_level_page():
                self.record_failure("Step 9: Service level page")
                return False

            if not self.step10_click_continue_button():
                self.record_failure("Step 10: Continue button")
                return False

            # Check current month's availability
            logger.info("=== Checking CURRENT month ===")
            if not self.step11_check_appointment_availability(month_label="current"):
                self.record_failure("Step 11: Check availability (current month)")
                return False

            # Try to check next month
            logger.info("=== Checking NEXT month ===")
            if self.step12_click_next_month():
                # Wait for next month to load
                self.wait_for_page_load()
                self.human_delay(2, 4)

                # Check availability in next month
                if not self.step11_check_appointment_availability(month_label="next"):
                    self.record_failure("Step 11: Check availability (next month)")
                    return False
            else:
                logger.info("No next month available to check")

            # SUCCESS: Reset failure count
            self.record_success()
            logger.info("🎉 All automation steps completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Unexpected error in execute_all_steps: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.record_failure(f"Unexpected error: {str(e)[:50]}")
            return False