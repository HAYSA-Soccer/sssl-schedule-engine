import json
import re
import requests
from bs4 import BeautifulSoup

URL = (
    "https://sssl.sportspilot.com/Scheduler/public/"
    "contests.aspx?header=on&smode=0&programid=1084&contest=2292"
)

html = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
).text

soup = BeautifulSoup(html, "html.parser")

teams = []

seen = set()

for link in soup.find_all("a"):

    text = link.get_text(" ", strip=True)

    if "HOLA" not in text.upper():
        continue

    href = link.get("href", "")

    # Example:
    # report.aspx?contest=2292&header=on&team=12197

    match = re.search(
        r"contest=(\d+).*?team=(\d+)",
        href
    )

    if not match:
        continue

    contest_id = int(match.group(1))
    team_id = int(match.group(2))

    key = (contest_id, team_id)

    if key in seen:
        continue

    seen.add(key)

    teams.append({
        "team_name": text,
        "contest_id": contest_id,
        "team_id": team_id,
        "url": (
            "https://sssl.sportspilot.com/Scheduler/public/"
            + href.lstrip("/")
        )
    })

print(json.dumps(
    sorted(teams, key=lambda x: x["team_name"]),
    indent=2
))
