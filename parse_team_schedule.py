import requests
from bs4 import BeautifulSoup
import json

url = (
    "https://sssl.sportspilot.com/Scheduler/public/"
    "report.aspx?contest=2292&header=on&team=12197"
)

html = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
).text

soup = BeautifulSoup(html, "html.parser")

schedule_table = soup.find_all("table")[12]

rows = schedule_table.find_all("tr")

games = []

for row in rows[1:]:  # skip header
    cols = [
        c.get_text(" ", strip=True)
        for c in row.find_all(["td", "th"])
    ]

    if len(cols) < 10:
        continue

    games.append({
        "event_id": cols[0],
        "date": cols[1],
        "start_time": cols[2],
        "end_time": cols[3],
        "day": cols[4],
        "location": cols[5],
        "visitor": cols[6],
        "visitor_score": cols[7],
        "home": cols[8],
        "home_score": cols[9],
    })

print(json.dumps(games, indent=2))
