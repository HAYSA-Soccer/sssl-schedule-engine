import requests
from bs4 import BeautifulSoup

url = (
    "https://sssl.sportspilot.com/Scheduler/public/"
    "report.aspx?contest=2292&header=on&team=12197"
)

html = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
).text

with open("debug.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Downloaded", len(html), "characters")

soup = BeautifulSoup(html, "html.parser")

print("Tables found:", len(soup.find_all("table")))
