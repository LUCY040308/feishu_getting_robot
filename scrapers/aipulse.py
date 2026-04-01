import requests
from bs4 import BeautifulSoup

def scrape_aipulse():
    url = "https://www.aipulse.run/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []
    for a in soup.select("a")[:30]:
        title = a.get_text().strip()
        link = a.get("href")

        if title and link and "http" in link:
            items.append((title, link))

    return items[:5]
