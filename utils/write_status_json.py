import json
from datetime import datetime


def write_status_json(
    all_games,
    ts_games,
    dashboard_rows
):

    create_count = sum(
        1
        for row in dashboard_rows
        if row.get("status") == "CREATE"
    )

    update_count = sum(
        1
        for row in dashboard_rows
        if row.get("status") == "UPDATE"
    )

    review_count = sum(
        1
        for row in dashboard_rows
        if row.get("status") == "REVIEW"
    )

    coverage = 0

    if len(all_games) > 0:
        coverage = round(
            (len(ts_games) / len(all_games)) * 100,
            1
        )

    status = "Healthy"

    if create_count > 0:
        status = "Attention Required"

    if len(ts_games) < len(all_games):
        status = "Catching Up"

    #
    # Team Status
    #

    teams = {}

    for game in all_games:

        team_name = game.get(
            "haysa_team",
            ""
        )

        if not team_name:
            continue

        teams[team_name] = {
            "name": team_name,
            "status": "good"
        }

    #
    # Mark teams with issues
    #

    for row in dashboard_rows:

        team_name = row.get(
            "team",
            ""
        )

        if (
            team_name
            and team_name in teams
        ):
            teams[team_name]["status"] = "warning"

    output = {

        "lastSync":
            datetime.now().strftime(
                "%Y-%m-%d %I:%M %p"
            ),

        "status":
            status,

        "ssslGames":
            len(all_games),

        "tsGames":
            len(ts_games),

        "coverage":
            coverage,

        "create":
            create_count,

        "update":
            update_count,

        "review":
            review_count,

        "teams":
            sorted(
                teams.values(),
                key=lambda x: x["name"]
            ),

        "issues":
            dashboard_rows

    }

    with open(
        "schedule-status.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print()
    print("=" * 60)
    print("SCHEDULE STATUS GENERATED")
    print("=" * 60)

    print(
        json.dumps(
            output,
            indent=2
        )
    )

    print("=" * 60)
