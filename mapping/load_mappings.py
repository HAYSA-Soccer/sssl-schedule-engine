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


def load_mappings():

    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(
        os.environ["GOOGLE_SHEET_ID"]
    )

    contest_sheet = spreadsheet.worksheet(
        "SSSL_Contest_List"
    )

    location_sheet = spreadsheet.worksheet(
        "Location_Mapping"
    )

    contest_rows = contest_sheet.get_all_records()

    location_rows = location_sheet.get_all_records()

    team_map = {}

    for row in contest_rows:

        sssl_name = (
            row.get("SSSL Team Name", "")
            .strip()
        )

        haysa_name = (
            row.get("TS Team Name", "")
            .strip()
        )

        if sssl_name:
            team_map[sssl_name] = haysa_name

    town_map = {}

    field_map = {}

    for row in location_rows:

        town = (
            row.get("Town Name", "")
            .strip()
        )

        abbreviation = (
            row.get("Town Abbreviation", "")
            .strip()
        )

        sssl_field = (
            row.get("SSSL Field Name", "")
            .strip()
        )

        ts_field_code = (
            row.get("TS Field Code", "")
            .strip()
        )

        friendly_field = (
            row.get("Friendly Field Name", "")
            .strip()
        )

        if abbreviation:
            town_map[abbreviation] = town

        if sssl_field:
            field_map[sssl_field] = {
                "ts_field_code": ts_field_code,
                "friendly_field_name": friendly_field
            }

    return {
        "team_map": team_map,
        "town_map": town_map,
        "field_map": field_map
    }
