# utils/write_status_json.py

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

        "issues":
            dashboard_rows

    }

    with open(
        "schedule_status.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print(
        "schedule_status.json generated"
    )
