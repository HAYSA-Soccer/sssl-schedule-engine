import re
import requests
from bs4 import BeautifulSoup

ROOT_URL = (
    "https://sssl.sportspilot.com/Scheduler/public/"
)

CONTEST_TREE_URL = (
    ROOT_URL +
    "contests.aspx?header=on&smode=0&programid=1084&contest=2292"
)


def discover_hola_teams():

    html = requests.get(
        CONTEST_TREE_URL,
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
            "team_id": team_id
        })

    return sorted(
        teams,
        key=lambda x: x["team_name"]
    )
