# run_automation.py
import os
import ssl
import certifi
import time
import logging
from tlscontact_steps import TLSContactSteps
from selenium.common.exceptions import NoSuchWindowException, WebDriverException  # ← added

# FIX SSL CERTIFICATES
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_stable_driver():
    """Create a stable Chrome driver with proper error handling"""
    try:
        import undetected_chromedriver as uc
        import platform  # ← added

        options = uc.ChromeOptions()

        # Essential stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # On macOS headful, disabling GPU can cause crashes; keep it for others
        if platform.system() != "Darwin":  # ← changed
            options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1400,900")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Disable password save popups and autofill COMPLETELY
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-autofill-keyboard-accessory-view")
        options.add_argument("--disable-features=PasswordSave")
        options.add_argument("--password-store=basic")
        options.add_argument("--disable-single-click-autofill")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-first-run")               # ← added
        options.add_argument("--no-default-browser-check")   # ← added

        # Experimental options to disable all password/autofill features
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
            "autofill.address_enabled": False,
            "password_manager_enabled": False,
            "enable-autofill": False,
        })

        # Add a small delay and use_subprocess for stability
        logger.info("Initializing Chrome driver...")
        driver = uc.Chrome(
            options=options,
            version_main=141,
            use_subprocess=True  # This helps with stability
        )

        # Set reasonable timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        logger.info("✅ Chrome driver initialized successfully!")
        return driver

    except Exception as e:
        logger.error(f"❌ Failed to create Chrome driver: {e}")
        return None


# ===== Helpers added below =====

def wait_for_cloudflare_or_recover(driver, seconds, url, recreate_driver_cb):
    """
    Keep session alive during CF wait; if window dies, recreate and reopen URL.
    """
    for _ in range(seconds):
        try:
            driver.execute_script("return 1")
        except NoSuchWindowException:
            logger.warning("⚠️ Window died during CF wait; recreating driver…")
            new_driver = recreate_driver_cb()
            if not new_driver:
                raise
            new_driver.get(url)
            driver = new_driver
        except WebDriverException:
            # transient hiccup; ignore
            pass
        time.sleep(1)
    return driver


def safe_switch_to_any_window(driver):
    handles = driver.window_handles
    if not handles:
        raise NoSuchWindowException("No window handles")
    driver.switch_to.window(handles[0])


def safe_current_url(driver):
    safe_switch_to_any_window(driver)
    return driver.current_url


def safe_title(driver):
    safe_switch_to_any_window(driver)
    return driver.title


def ensure_window_alive(driver, url=None, recreate_driver_cb=None):
    try:
        _ = driver.window_handles
        if not driver.window_handles:
            raise NoSuchWindowException("No window handles")
        safe_switch_to_any_window(driver)
        return driver
    except NoSuchWindowException:
        logger.warning("⚠️ No window alive; recreating driver…")
        if recreate_driver_cb and url:
            new_driver = recreate_driver_cb()
            if not new_driver:
                raise
            new_driver.get(url)
            return new_driver
        raise

# ===== End helpers =====


def main():
    driver = None
    try:
        logger.info("🚀 Starting TLSContact Automation...")

        # Create stable driver
        driver = create_stable_driver()
        if not driver:
            logger.error("❌ Could not initialize browser")
            return

        # Add a small delay after driver creation
        time.sleep(2)

        # Navigate to the specific URL
        url = "https://visas-fr.tlscontact.com/en-us/country/am/vac/amEVN2fr"
        logger.info(f"🌐 Navigating to: {url}")

        try:
            driver.get(url)
            logger.info("✅ Page navigation successful")
        except Exception as nav_error:
            logger.error(f"❌ Navigation failed: {nav_error}")
            # Try one more time
            try:
                driver.get(url)
                logger.info("✅ Second navigation attempt successful")
            except Exception as retry_error:
                logger.error(f"❌ Both navigation attempts failed: {retry_error}")
                return

        logger.info("⏳ Waiting for Cloudflare (30 seconds)...")
        # time.sleep(30)  # ← removed
        driver = wait_for_cloudflare_or_recover(driver, 30, url, create_stable_driver)  # ← added

        # Ensure we still have a window
        driver = ensure_window_alive(driver, url, create_stable_driver)  # ← added

        # Check current status
        try:  # ← added
            current_url = safe_current_url(driver)
            page_title = safe_title(driver)
        except NoSuchWindowException:
            logger.error("❌ Window closed before reading URL/title. Recreating…")
            driver = create_stable_driver()
            if not driver:
                return
            driver.get(url)
            current_url = safe_current_url(driver)
            page_title = safe_title(driver)

        logger.info(f"📄 Current URL: {current_url}")
        logger.info(f"📄 Page title: {page_title}")

        # Just continue regardless of Cloudflare status
        logger.info("🎉 Continuing with automation steps...")

        # Initialize steps automator
        automator = TLSContactSteps(driver)

        try:
            automator.take_screenshot("after_cloudflare.png")
        except Exception:
            logger.warning("Could not take initial screenshot")

        # Wait for page to load completely
        if not automator.wait_for_page_load():
            logger.warning("Page load timeout, but continuing...")

        # Execute all steps automatically
        logger.info("Starting automatic step execution...")
        success = automator.execute_all_steps()

        if success:
            logger.info("🎉 All automation steps completed successfully!")
            try:
                automator.take_screenshot("final_success.png")
            except Exception:
                pass
        else:
            logger.error("❌ Some steps failed - check the logs and screenshots")

        # Keep browser open for inspection
        logger.info("🖥️ Browser will remain open for 60 seconds...")
        time.sleep(60)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())

    finally:
        if driver:
            try:
                driver.quit()
                logger.info("🔚 Browser closed.")
            except Exception:
                logger.info("Browser already closed or couldn't be closed properly.")


if __name__ == "__main__":
    main()
