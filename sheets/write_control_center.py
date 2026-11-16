import json
import os

import gspread

from google.oauth2.service_account import Credentials
from datetime import datetime


SERVICE_ACCOUNT_INFO = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"]
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def write_control_center(
    all_games,
    ts_games,
    dashboard_rows
):

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
            "Control_Center"
        )

    except gspread.exceptions.WorksheetNotFound:

        sheet = spreadsheet.add_worksheet(
            title="Control_Center",
            rows=500,
            cols=20
        )

    create_count = sum(
        1 for r in dashboard_rows
        if r["status"] == "CREATE"
    )

    update_count = sum(
        1 for r in dashboard_rows
        if r["status"] == "UPDATE"
    )

    review_count = sum(
        1 for r in dashboard_rows
        if r["status"] == "REVIEW"
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %I:%M %p"
    )

    rows = [

        ["
