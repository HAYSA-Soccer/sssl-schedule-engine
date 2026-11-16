from datetime import datetime


def normalize_date(value):

    if not value:
        return ""

    value = str(value).strip()

    for fmt in (
        "%m/%d/%Y",
        "%Y-%m-%d"
    ):
        try:
            return datetime.strptime(
                value,
                fmt
            ).strftime("%Y-%m-%d")
        except ValueError:
            pass

    return value


def normalize_time(value):

    if not value:
        return ""

    value = str(value).strip()

    for fmt in (
        "%I:%M %p",
        "%H:%M"
    ):
        try:
            return datetime.strptime(
                value,
                fmt
            ).strftime("%H:%M")
        except ValueError:
            pass

    return value


def build_ts_game(game):

    return {

        "raw_matchup":
            str(
                game.get(
                    "summary",
                    ""
                )
            ).strip(),

        "ts_team":
            str(
                game.get(
                    "team",
                    ""
                )
            ).strip(),

        "ts_opponent":
            str(
                game.get(
                    "opponent",
                    ""
                )
            ).strip(),

        "ts_home_away":
            str(
                game.get(
                    "home_away",
                    ""
                )
            ).strip(),

        "ts_date":
            normalize_date(
                game.get(
                    "date",
                    ""
                )
            ),

        "ts_time":
            normalize_time(
                game.get(
                    "start_time",
                    ""
                )
            ),

        "ts_field":
            "",

        "ts_field_display":
            str(
                game.get(
                    "location",
                    ""
                )
            ).strip(),

        "event_id":
            game.get(
                "event_id",
                ""
            ),

        "calendar_event_id":
            ""
    }


def generate_dashboard(
    sssl_games,
    ts_games_sheet
):

    dashboard_rows = []

    ts_games = []

    for game in ts_games_sheet:

        ts_games.append(
            build_ts_game(
                game
            )
        )

    ts_lookup = {}

    for game in ts_games:

        key = (

            game["ts_team"].strip(),

            game["ts_opponent"].strip(),

            game["ts_date"]

        )

        ts_lookup[key] = game

    for sssl_game in sssl_games:

        sssl_team = (
            sssl_game.get(
                "haysa_team",
                ""
            )
            .strip()
        )

        sssl_opponent = (
            sssl_game.get(
                "opponent_town",
                ""
            )
            .strip()
        )

        sssl_date = normalize_date(
            sssl_game.get(
                "date",
                ""
            )
        )

        key = (
            sssl_team,
            sssl_opponent,
            sssl_date
        )

        ts_game = ts_lookup.get(
            key
        )

        if not ts_game:

            dashboard_rows.append({

                "status":
                    "CREATE",

                "team":
                    sssl_team,

                "opponent":
                    sssl_opponent,

                "sssl_date":
                    sssl_game.get(
                        "date",
                        ""
                    ),

                "sssl_time":
                    sssl_game.get(
                        "start_time",
                        ""
                    ),

                "sssl_field":
                    sssl_game.get(
                        "ts_field_code",
                        ""
                    ),

                "raw_matchup":
                    "",

                "ts_team":
                    "",

                "ts_opponent":
                    "",

                "ts_date":
                    "",

                "ts_time":
                    "",

                "ts_field":
                    "",

                "ts_field_display":
                    "",

                "action_required":
                    "Create TeamSideline game",

                "event_id":
                    ""

            })

            continue

        changes = []

        sssl_time = normalize_time(
            sssl_game.get(
                "start_time",
                ""
            )
        )

        if (
            sssl_time
            and ts_game["ts_time"]
            and sssl_time != ts_game["ts_time"]
        ):

            changes.append(
                f"Time: {ts_game['ts_time']} -> {sssl_time}"
            )

        if changes:

            dashboard_rows.append({

                "status":
                    "UPDATE",

                "team":
                    sssl_team,

                "opponent":
                    sssl_opponent,

                "sssl_date":
                    sssl_game.get(
                        "date",
                        ""
                    ),

                "sssl_time":
                    sssl_game.get(
                        "start_time",
                        ""
                    ),

                "sssl_field":
                    sssl_game.get(
                        "ts_field_code",
                        ""
                    ),

                "raw_matchup":
                    ts_game["raw_matchup"],

                "ts_team":
                    ts_game["ts_team"],

                "ts_opponent":
                    ts_game["ts_opponent"],

                "ts_date":
                    ts_game["ts_date"],

                "ts_time":
                    ts_game["ts_time"],

                "ts_field":
                    ts_game["ts_field"],

                "ts_field_display":
                    ts_game["ts_field_display"],

                "action_required":
                    "; ".join(
                        changes
                    ),

                "event_id":
                    ts_game[
                        "calendar_event_id"
                    ]

            })

    sssl_keys = {

        (

            game.get(
                "haysa_team",
                ""
            ).strip(),

            game.get(
                "opponent_town",
                ""
            ).strip(),

            normalize_date(
                game.get(
                    "date",
                    ""
                )
            )

        )

        for game in sssl_games

    }

    for ts_game in ts_games:

        key = (

            ts_game["ts_team"].strip(),

            ts_game["ts_opponent"].strip(),

            ts_game["ts_date"]

        )

        if key not in sssl_keys:

            dashboard_rows.append({

                "status":
                    "REVIEW",

                "team":
                    "",

                "opponent":
                    "",

                "sssl_date":
                    "",

                "sssl_time":
                    "",

                "sssl_field":
                    "",

                "raw_matchup":
                    ts_game["raw_matchup"],

                "ts_team":
                    ts_game["ts_team"],

                "ts_opponent":
                    ts_game["ts_opponent"],

                "ts_date":
                    ts_game["ts_date"],

                "ts_time":
                    ts_game["ts_time"],

                "ts_field":
                    ts_game["ts_field"],

                "ts_field_display":
                    ts_game["ts_field_display"],

                "action_required":
                    "Exists in TeamSideline but not in SSSL",

                "event_id":
                    ts_game[
                        "calendar_event_id"
                    ]

            })

    dashboard_rows.sort(
        key=lambda x: (
            x["status"],
            x.get(
                "team",
                ""
            ),
            x.get(
                "sssl_date",
                ""
            )
        )
    )

    return dashboard_rows
