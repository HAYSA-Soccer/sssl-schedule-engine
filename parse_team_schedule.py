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

soup = BeautifulSoup(html, "html.parser")

tables = soup.find_all("table")

schedule_table = tables[12]

rows = schedule_table.find_all("tr")

print(f"Rows found: {len(rows)}")

for i, row in enumerate(rows[:15]):
    cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]

    print()
    print(f"ROW {i}")
    print(cols)
