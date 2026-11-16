import json
import os

import gspread

from google.oauth2.service_account import Credentials

from sssl.discover_hola_teams import discover_hola_teams
from sssl.fetch_team_schedule import fetch_team_schedule

from sheets.write_games import write_games_to_sheet
from sheets.write_dashboard import write_dashboard_to_sheet
from sheets.write_control_center import (
    write_control_center
)

from audit.generate_dashboard import generate_dashboard
from mapping.load_mappings import load_mappings

from utils.write_status_json import (
    write_status_json
)


SERVICE_ACCOUNT_INFO = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"]
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def main():

    teams = discover_hola_teams()

    mappings = load_mappings()

    team_map = mappings["team_map"]
    town_map = mappings["town_map"]
    field_map = mappings["field_map"]

    print()
    print("=" * 60)
    print(f"Found {len(teams)} HOLA teams")
    print("=" * 60)
    print()

    unique_games = {}

    for team in teams:

        team_name = team["team_name"]
        contest_id = team["contest_id"]
        team_id = team["team_id"]

        print(f"Fetching: {team_name}")

        games = fetch_team_schedule(
            contest_id,
            team_id
        )

        print(f"  Found {len(games)} games")

        for game in games:

            game["hola_team"] = team_name

            division = team_name

            if division.startswith("HOLA "):
                division = division[5:]

            if "(" in division:
                division = division.split("(")[0].strip()

            game["division"] = division

            game["hola_is_home"] = (
                "HOLA" in game["home"].upper()
            )

            #
            # Team translation
            #

            game["haysa_team"] = team_map.get(
                team_name,
                ""
            )

            #
            # Opponent translation
            #

            if game["hola_is_home"]:
                opponent_team = game["visitor"]
            else:
                opponent_team = game["home"]

            opponent_code = (
                opponent_team.strip().split()[0]
                if opponent_team.strip()
                else ""
            )

            game["opponent_town"] = town_map.get(
                opponent_code,
                opponent_code
            )

            #
            # Field translation
            #

            location_text = game.get(
                "location",
                ""
            ).strip()

            field_info = field_map.get(
                location_text
            )

            if not field_info:

                sssl_field = ""

                if "/" in location_text:
                    sssl_field = (
                        location_text
                        .split("/")[-1]
                        .strip()
                    )
                else:
                    sssl_field = location_text

                field_info = field_map.get(
                    sssl_field,
                    {}
                )

            game["ts_field_code"] = field_info.get(
                "ts_field_code",
                ""
            )

            game["friendly_field_name"] = field_info.get(
                "friendly_field_name",
                ""
            )

            unique_games[
                game["event_id"]
            ] = game

    all_games = list(
        unique_games.values()
    )

    all_games.sort(
        key=lambda x: (
            x["date"],
            x["start_time"]
        )
    )

    print()
    print("=" * 60)
    print(
        f"TOTAL UNIQUE GAMES: "
        f"{len(all_games)}"
    )
    print("=" * 60)
    print()

    with open(
        "all_games.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_games,
            f,
            indent=2
        )

    print("Saved all_games.json")

    print()
    print("Writing SSSL_Games sheet...")
    print()

    write_games_to_sheet(
        all_games
    )

    #
    # Dashboard Generation
    #

    print()
    print("Loading TS_Games...")
    print()

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

    ts_games_sheet = spreadsheet.worksheet(
        "TS_Games"
    )

    ts_games = (
        ts_games_sheet.get_all_records()
    )

    print(
        f"Loaded {len(ts_games)} TS game rows"
    )

    print()
    print("Generating Dashboard...")
    print()

    dashboard_rows = generate_dashboard(
        all_games,
        ts_games
    )

    write_dashboard_to_sheet(
        dashboard_rows
    )

    print(
        f"Dashboard updated with "
        f"{len(dashboard_rows)} items"
    )

    #
    # Control Center
    #

    print()
    print("Updating Control_Center...")
    print()

    write_control_center(
        all_games,
        ts_games,
        dashboard_rows
    )

    write_status_json(
        all_games,
        ts_games,
        dashboard_rows
    )

    print(
        "Control_Center updated."
    )

    print()
    print("First 5 games:")
    print()

    print(
        json.dumps(
            all_games[:5],
            indent=2
        )
    )


if __name__ == "__main__":
    main()
