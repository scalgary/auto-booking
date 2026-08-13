import argparse
import logging
import os
import smtplib
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

CALENDAR_URL = (
    "https://tickets.getty.edu/Online/default.asp"
    "?BOparam::WSconstant::permalink=villa&BOparam::WSconstant::context_id="
)
TIME_SLEEP = 15

EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def check_date_open(target_date: datetime) -> bool:
    """Check if a specific date has a clickable calendar-date-button.

    Matches by aria-label (e.g. 'See events for August 13') to avoid
    confusing days with the same number across different months.
    """
    label_fragment = target_date.strftime("%B %-d")  # e.g. "January 2"

    driver = get_driver()
    wait = WebDriverWait(driver, TIME_SLEEP)

    try:
        logger.info(f"Opening {CALENDAR_URL}")
        driver.get(CALENDAR_URL)

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.calendar-container")))
        time.sleep(1)  # allow calendar to fully render

        open_buttons = driver.find_elements(
            By.CSS_SELECTOR, "button.calendar-date-button"
        )

        open_labels = [
            b.get_attribute("aria-label") or "" for b in open_buttons
        ]
        logger.info(f"Open days visible: {open_labels}")

        is_open = any(label_fragment in label for label in open_labels)
        logger.info(f"{target_date.strftime('%B %d, %Y')} open: {is_open}")
        return is_open

    except TimeoutException:
        logger.error("Timeout waiting for calendar to load")
        return False

    finally:
        driver.quit()


def send_alert_email(target_date: datetime):
    if not all([EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD]):
        logger.error("Email configuration missing")
        return False

    date_str = target_date.strftime("%B %d, %Y")
    subject = f"Getty Villa - {date_str} is open!"
    body = f"{date_str} is now open for booking.\n\n"
    body += f"Book here: {CALENDAR_URL}\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        logger.info(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Alert email sent to {EMAIL_TO}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def parse_args():
    parser = argparse.ArgumentParser(description="Check if a date is open on Getty Villa calendar")
    parser.add_argument(
        "--date",
        required=True,
        help="Target date, format YYYY-MM-DD, e.g. 2026-09-20",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    target_date = datetime.strptime(args.date, "%Y-%m-%d")

    is_open = check_date_open(target_date)

    if is_open:
        send_alert_email(target_date)
    else:
        logger.info(f"{target_date.strftime('%B %d, %Y')} not open yet. No email sent.")


if __name__ == "__main__":
    main()