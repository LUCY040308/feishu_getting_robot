import requests
from bs4 import BeautifulSoup

def scrape_ai_bot():
    url = "https://ai-bot.cn/daily-ai-news/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []
    for a in soup.select("article h2 a")[:5]:
        title = a.get_text()
        link = a["href"]
        items.append((title, link))

    return items
