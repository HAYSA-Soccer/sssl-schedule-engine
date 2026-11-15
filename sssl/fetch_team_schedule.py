import requests
from bs4 import BeautifulSoup


ROOT_URL = (
    "https://sssl.sportspilot.com/Scheduler/public/"
)


def fetch_team_schedule(contest_id, team_id):

    url = (
        ROOT_URL
        + f"report.aspx?contest={contest_id}"
        + f"&header=on&team={team_id}"
    )

    html = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    ).text

    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")

    if len(tables) < 13:
        return []

    schedule_table = tables[12]

    rows = schedule_table.find_all("tr")

    games = []

    for row in rows[1:]:

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

    return games
