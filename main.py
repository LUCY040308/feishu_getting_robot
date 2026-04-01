from __future__ import annotations

import datetime
import os
from pathlib import Path

import requests

from scrapers.ai_bot import scrape_ai_bot
from scrapers.aipulse import scrape_aipulse
from scrapers.rss import scrape_rss

BASE_DIR = Path(__file__).resolve().parent
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "").strip()
WEB_SOURCES_FILE = Path(os.getenv("WEB_SOURCES_FILE", str(BASE_DIR / "web_sources.txt")))
HISTORY_FILE = Path(os.getenv("HISTORY_FILE", str(BASE_DIR / "history.txt")))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
REQUEST_TIMEOUT = 20

SCRAPER_MAP = {
    "ai_bot": scrape_ai_bot,
    "aipulse": scrape_aipulse,
    "ai": scrape_rss,
    "rss": scrape_rss,
}


def load_history() -> set[str]:
    if not HISTORY_FILE.exists():
        return set()

    with HISTORY_FILE.open("r", encoding="utf-8") as history_file:
        return {line.strip() for line in history_file if line.strip()}


def save_history(history: set[str]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with HISTORY_FILE.open("w", encoding="utf-8") as history_file:
        for entry in sorted(history):
            history_file.write(entry + "\n")


def load_sources():
    with WEB_SOURCES_FILE.open("r", encoding="utf-8") as sources_file:
        for raw_line in sources_file:
            line = raw_line.strip()
            if not line:
                continue

            try:
                name, url = line.split("|", 1)
            except ValueError:
                print(f"Format error: {raw_line.rstrip()}")
                continue

            yield name.strip(), url.strip()


def collect_new_items(history: set[str]) -> list[str]:
    new_items = []

    for name, url in load_sources():
        scraper = SCRAPER_MAP.get(name)
        if scraper is None:
            print(f"Missing scraper: {name}")
            continue

        try:
            results = scraper(url)
        except Exception as exc:
            print(f"{name} scrape failed: {exc}")
            continue

        for title, link in results:
            entry_id = f"{title}|{link}"
            if entry_id in history:
                continue

            new_items.append(f"[{name}] {title}\n{link}")
            history.add(entry_id)

    return new_items


def build_message(new_items: list[str]) -> str | None:
    message_items = list(new_items)

    if DEBUG:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_items.append(f"Debug message\nTime: {now}")

    if not message_items:
        return None

    return "AI web updates\n\n" + "\n\n".join(message_items)


def send_to_feishu(message: str) -> str:
    if not FEISHU_WEBHOOK:
        raise ValueError("FEISHU_WEBHOOK environment variable is not set.")

    data = {
        "msg_type": "text",
        "content": {"text": message},
    }

    response = requests.post(FEISHU_WEBHOOK, json=data, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    print("Feishu response:", response.text)
    return response.text


def run_job() -> dict[str, int | bool]:
    history = load_history()
    new_items = collect_new_items(history)
    message = build_message(new_items)

    if not message:
        print("No new content")
        save_history(history)
        return {"sent": False, "new_items": 0}

    send_to_feishu(message)
    save_history(history)
    return {"sent": True, "new_items": len(new_items)}


def main() -> None:
    result = run_job()
    print("Run result:", result)


if __name__ == "__main__":
    main()
