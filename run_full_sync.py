import json

from sssl.discover_hola_teams import discover_hola_teams
from sssl.fetch_team_schedule import fetch_team_schedule
from sheets.write_games import write_games_to_sheet


def main():

    teams = discover_hola_teams()

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

            unique_games[game["event_id"]] = game

    all_games = list(unique_games.values())

    all_games.sort(
        key=lambda x: (
            x["date"],
            x["start_time"]
        )
    )

    print()
    print("=" * 60)
    print(f"TOTAL UNIQUE GAMES: {len(all_games)}")
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
