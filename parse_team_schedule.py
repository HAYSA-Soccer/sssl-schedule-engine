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

print(f"Found {len(tables)} tables")

for i, table in enumerate(tables):
    text = table.get_text(" ", strip=True)

    print("\n" + "=" * 80)
    print(f"TABLE {i}")
    print("=" * 80)

    print(text[:1000])
