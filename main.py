import requests
import os
import datetime

from scrapers.ai_bot import scrape_ai_bot
from scrapers.aipulse import scrape_aipulse

# ======================
# 🔧 配置区
# ======================

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/ef3b9cf6-10d9-4169-8d7d-e31f1339f444"
WEB_SOURCES_FILE = "web_sources.txt"
HISTORY_FILE = "history.txt"

DEBUG = True  # 👉 调试模式：每次都会发消息

# ======================
# 🧠 抓取器映射
# ======================

SCRAPER_MAP = {
    "ai_bot": scrape_ai_bot,
    "aipulse": scrape_aipulse,
}

# ======================
# 📦 读取历史记录（去重）
# ======================

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = set(line.strip() for line in f)
else:
    history = set()

new_items = []

# ======================
# 🌐 抓取网站
# ======================

with open(WEB_SOURCES_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        try:
            name, url = line.strip().split("|")
        except ValueError:
            print(f"格式错误: {line}")
            continue

        scraper = SCRAPER_MAP.get(name)

        if not scraper:
            print(f"未找到抓取器: {name}")
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

# ======================
# 🧪 DEBUG 模式（强制发消息）
# ======================

if DEBUG:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_items.append(f"🧪 调试消息\n时间：{now}")

# ======================
# 📤 推送飞书
# ======================

if new_items:
    message = "🚀 AI网页情报更新\n\n" + "\n\n".join(new_items)

    data = {
        "msg_type": "text",
        "content": {"text": message}
    }

    try:
        resp = requests.post(FEISHU_WEBHOOK, json=data)
        print("飞书返回:", resp.text)
    except Exception as e:
        print("发送失败:", e)
else:
    print("没有新内容")

# ======================
# 💾 保存历史记录
# ======================

with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    for line in history:
        f.write(line + "\n")
