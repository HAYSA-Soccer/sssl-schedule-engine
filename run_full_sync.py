import json

from sssl.discover_hola_teams import (
    discover_hola_teams
)

from sssl.fetch_team_schedule import (
    fetch_team_schedule
)


def main():

    teams = discover_hola_teams()

    print()
    print(f"Found {len(teams)} HOLA teams")
    print()

    all_games = []

    for team in teams:

        print(
            f"Fetching {team['team_name']}"
        )

        games = fetch_team_schedule(
            team["contest_id"],
            team["team_id"]
        )

        print(
            f"  Found {len(games)} games"
        )

        all_games.extend(games)

    print()
    print(
        f"Total Games Retrieved: {len(all_games)}"
    )

    print()

    print(
        json.dumps(
            all_games,
            indent=2
        )[:5000]
    )


if __name__ == "__main__":
    main()
