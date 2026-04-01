import requests
import os
from scrapers.ai_bot import scrape_ai_bot
from scrapers.aipulse import scrape_aipulse

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/ef3b9cf6-10d9-4169-8d7d-e31f1339f444"

HISTORY_FILE = "history.txt"

# 读取历史
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = set(line.strip() for line in f)
else:
    history = set()

new_items = []

# 所有抓取器
scrapers = [scrape_ai_bot, scrape_aipulse]

for scraper in scrapers:
    try:
        results = scraper()
        for title, link in results:
            entry_id = title + link
            if entry_id not in history:
                new_items.append(f"📰 {title}\n{link}")
                history.add(entry_id)
    except Exception as e:
        print(f"抓取失败: {e}")

# 推送飞书
if new_items:
    message = "🚀 AI 网页情报更新\n\n" + "\n\n".join(new_items)
    data = {
        "msg_type": "text",
        "content": {"text": message}
    }
    resp = requests.post(FEISHU_WEBHOOK, json=data)
    print(resp.text)

# 保存历史
with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    for line in history:
        f.write(line + "\n")
