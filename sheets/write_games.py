import json
import os

import gspread

from google.oauth2.service_account import Credentials


SERVICE_ACCOUNT_INFO = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"]
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def write_games_to_sheet(games):

    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(
        os.environ["GOOGLE_SHEET_ID"]
    )

    sheet = spreadsheet.worksheet(
        "SSSL_Games"
    )

    header = [
        "event_id",
        "date",
        "start_time",
        "end_time",
        "day",
        "division",
        "hola_team",
        "haysa_team",
        "opponent_town",
        "ts_field_code",
        "friendly_field_name",
        "hola_is_home",
        "visitor",
        "visitor_score",
        "home",
        "home_score",
        "location"
    ]

    rows = []

    for g in games:

        rows.append([
            g.get("event_id", ""),
            g.get("date", ""),
            g.get("start_time", ""),
            g.get("end_time", ""),
            g.get("day", ""),
            g.get("division", ""),
            g.get("hola_team", ""),
            g.get("haysa_team", ""),
            g.get("opponent_town", ""),
            g.get("ts_field_code", ""),
            g.get("friendly_field_name", ""),
            str(g.get("hola_is_home", False)),
            g.get("visitor", ""),
            g.get("visitor_score", ""),
            g.get("home", ""),
            g.get("home_score", ""),
            g.get("location", "")
        ])

    sheet.clear()

    sheet.append_row(header)

    if rows:
        sheet.append_rows(
            rows,
            value_input_option="USER_ENTERED"
        )

    print(
        f"Wrote {len(rows)} games to SSSL_Games"
    )
