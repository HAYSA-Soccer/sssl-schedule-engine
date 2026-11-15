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


def write_dashboard_to_sheet(rows):

    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(
        os.environ["GOOGLE_SHEET_ID"]
    )

    try:
        sheet = spreadsheet.worksheet(
            "Dashboard"
        )
    except Exception:
        sheet = spreadsheet.add_worksheet(
            title="Dashboard",
            rows=1000,
            cols=20
        )

    header = [
        "status",
        "team",
        "opponent",
        "action_required",
        "event_id"
    ]

    data = []

    for row in rows:

        data.append([
            row.get("status", ""),
            row.get("team", ""),
            row.get("opponent", ""),
            row.get("action_required", ""),
            row.get("event_id", "")
        ])

    sheet.clear()

    sheet.append_row(header)

    if data:
        sheet.append_rows(
            data,
            value_input_option="USER_ENTERED"
        )

    print(
        f"Wrote {len(data)} dashboard items"
    )
