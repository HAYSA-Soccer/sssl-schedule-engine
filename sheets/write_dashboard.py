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

    client = gspread.authorize(
        creds
    )

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
            rows=2000,
            cols=30
        )

    header = [

        "status",

        "team",
        "opponent",

        "raw_matchup",

        "ts_team",
        "ts_opponent",

        "sssl_date",
        "ts_date",

        "sssl_time",
        "ts_time",

        "sssl_field",
        "ts_field",

        "ts_field_display",

        "action_required",

        "event_id"

    ]

    data = []

    for row in rows:

        data.append([

            row.get(
                "status",
                ""
            ),

            row.get(
                "team",
                ""
            ),

            row.get(
                "opponent",
                ""
            ),


            row.get(
                "raw_matchup",
                ""
            ),

            row.get(
                "ts_team",
                ""
            ),

            row.get(
                "ts_opponent",
                ""
            ),

            row.get(
                "sssl_date",
                ""
            ),

            row.get(
                "ts_date",
                ""
            ),

            row.get(
                "sssl_time",
                ""
            ),

            row.get(
                "ts_time",
                ""
            ),

            row.get(
                "sssl_field",
                ""
            ),

            row.get(
                "ts_field",
                ""
            ),

            row.get(
                "ts_field_display",
                ""
            ),

            row.get(
                "action_required",
                ""
            ),

            row.get(
                "event_id",
                ""
            )

        ])

    sheet.clear()

    sheet.append_row(
        header
    )

    if data:

        sheet.append_rows(
            data,
            value_input_option="USER_ENTERED"
        )

    print(
        f"Wrote {len(data)} dashboard items"
    )
