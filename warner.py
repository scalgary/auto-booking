import requests
from bs4 import BeautifulSoup
import re
import os
import json
import logging
import smtplib
import time
from email.mime.text import MIMEText

URL = "https://www.wbstudiotour.com/news/"
SNAPSHOT_FILE = "last_snapshot.json"
LOG_FILE = "news_checker.log"

GMAIL_USER = os.environ.get("EMAIL_FROM")
GMAIL_APP_PASSWORD = os.environ.get("EMAIL_PASSWORD")
ALERT_TO = os.environ.get("EMAIL_TO")
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("news_checker")

def send_email(subject, body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.warning("Email credentials missing, skipping email.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = ALERT_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, [ALERT_TO], msg.as_string())
    logger.info("Email sent to %s", ALERT_TO)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10

def fetch_page_lines():
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(URL, timeout=15, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            full_text = soup.get_text(separator="\n", strip=True)
            return [line for line in full_text.split("\n") if line.strip()]
        except requests.exceptions.RequestException as e:
            last_error = e
            logger.warning("Attempt %d/%d failed: %s", attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
    raise last_error

def parse_news_items(lines):
    items = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("Posted in"):
            title = lines[i - 1] if i > 0 else ""
            date_match = re.search(r"on (\d{1,2}/\d{1,2}/\d{4})", lines[i])
            date = date_match.group(1) if date_match else ""

            j = i + 1
            excerpt_lines = []
            while j < len(lines) and lines[j] != "Read more":
                excerpt_lines.append(lines[j])
                j += 1
            excerpt = " ".join(excerpt_lines)

            items.append({"title": title, "date": date, "excerpt": excerpt})
            i = j
        i += 1
    return items

def load_previous_titles():
    if not os.path.exists(SNAPSHOT_FILE):
        return None
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(item["title"] for item in data)

def save_snapshot(items):
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def main():
    logger.info("Starting news check for %s", URL)

    lines = fetch_page_lines()
    items = parse_news_items(lines)
    logger.info("Found %d news items on the page.", len(items))

    previous_titles = load_previous_titles()

    if previous_titles is None:
        logger.info("First run. No previous snapshot found. Saving current state.")
        new_items = []
    else:
        new_items = [item for item in items if item["title"] not in previous_titles]

    if new_items:
        logger.info("NEW ITEM(S) DETECTED: %d", len(new_items))
        for item in new_items:
            logger.info("New: [%s] %s", item["date"], item["title"])

        body_lines = [f"[{item['date']}] {item['title']}\n{item['excerpt']}\n" for item in new_items]
        send_email(
            subject=f"WB Studio Tour: {len(new_items)} new item(s)",
            body="New items found:\n\n" + "\n".join(body_lines)
        )
    elif previous_titles is not None:
        logger.info("No new items.")
        if TEST_MODE:
            logger.info("TEST_MODE is on, sending test email despite no change.")
            send_email(
                subject="WB Studio Tour: TEST email (no real change)",
                body="This is a test email. No new items were actually found."
            )

    save_snapshot(items)
    logger.info("Snapshot updated. Done.")

    return new_items

if __name__ == "__main__":
    main()