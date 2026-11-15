import requests

URL = (
    "https://sssl.sportspilot.com/Scheduler/public/"
    "report.aspx?contest=2292&header=on&team=12197"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0 Safari/537.36"
    )
}

r = requests.get(URL, headers=headers, timeout=30)

print("STATUS:", r.status_code)
print("PAGE LENGTH:", len(r.text))
print("CONTAINS HOLA:", "HOLA" in r.text)
print("CONTAINS BAIRD:", "Baird" in r.text)
print("CONTAINS HOLBROOK:", "Holbrook" in r.text)
print("CONTAINS VISITOR:", "Visitor" in r.text)
print("CONTAINS HOME:", "Home" in r.text)
