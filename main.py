from scrapers.ai_bot import scrape_ai_bot
from scrapers.aipulse import scrape_aipulse

SCRAPER_MAP = {
    "ai_bot": scrape_ai_bot,
    "aipulse": scrape_aipulse,
}

WEB_SOURCES_FILE = "web_sources.txt"

new_items = []

with open(WEB_SOURCES_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        name, url = line.strip().split("|")

        scraper = SCRAPER_MAP.get(name)

        if not scraper:
            continue

        try:
            results = scraper(url)
            for title, link in results:
                entry_id = title + link
                if entry_id not in history:
                    new_items.append(f"🌐 {title}\n{link}")
                    history.add(entry_id)
        except Exception as e:
            print(f"{name} 抓取失败: {e}")
