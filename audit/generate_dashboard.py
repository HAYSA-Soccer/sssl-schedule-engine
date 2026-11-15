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


def build_ts_game(event):

    matchup = event.get(
        "team",
        ""
    ).strip()

    ts_team = ""
    ts_opponent = ""

    if " vs. " in matchup:

        ts_team, ts_opponent = matchup.split(
            " vs. ",
            1
        )

    return {

        "ts_team":
            ts_team.strip(),

        "ts_opponent":
            ts_opponent.strip(),

        "ts_date":
            normalize_date(
                event.get(
                    "date",
                    ""
                )
            ),

        "ts_time":
            normalize_time(
                event.get(
                    "start_time",
                    ""
                )
            ),

        "ts_field":
            event.get(
                "field",
                ""
            ).strip(),

        "ts_field_display":
            event.get(
                "field_display",
                ""
            ).strip(),

        "event_id":
            event.get(
                "event_id",
                ""
            ),

        "calendar_event_id":
            event.get(
                "calendar_event_id",
                ""
            )

    }


def generate_dashboard(
    sssl_games,
    events
):

    dashboard_rows = []

    #
    # Active TS Game Events
    #

    ts_games = []

    for event in events:

        if (
            event.get("type") == "game"
            and event.get("status") == "active"
        ):

            ts_games.append(
                build_ts_game(
                    event
                )
            )

    #
    # Lookup
    #

    ts_lookup = {}

    for game in ts_games:

        key = (
            game["ts_team"],
            game["ts_opponent"]
        )

        ts_lookup[key] = game

    #
    # Compare SSSL -> TS
    #

    for sssl_game in sssl_games:

        key = (

            sssl_game.get(
                "haysa_team",
                ""
            ),

            sssl_game.get(
                "opponent_town",
                ""
            )

        )

        ts_game = ts_lookup.get(
            key
        )

        #
        # Missing from TS
        #

        if not ts_game:

            dashboard_rows.append({

                "status": "CREATE",

                "team":
                    sssl_game.get(
                        "haysa_team",
                        ""
                    ),

                "opponent":
                    sssl_game.get(
                        "opponent_town",
                        ""
                    ),

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

                "ts_team": "",

                "ts_opponent": "",

                "ts_date": "",

                "ts_time": "",

                "ts_field": "",

                "ts_field_display": "",

                "action_required":
                    "Create TeamSideline game",

                "event_id": ""

            })

            continue

        changes = []

        sssl_date = normalize_date(
            sssl_game.get(
                "date",
                ""
            )
        )

        if (
            sssl_date
            and ts_game["ts_date"]
            and sssl_date != ts_game["ts_date"]
        ):

            changes.append(
                f"Date: "
                f"{ts_game['ts_date']} -> "
                f"{sssl_date}"
            )

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
                f"Time: "
                f"{ts_game['ts_time']} -> "
                f"{sssl_time}"
            )

        sssl_field = (
            sssl_game.get(
                "ts_field_code",
                ""
            )
            .strip()
        )

        if (
            sssl_field
            and ts_game["ts_field"]
            and sssl_field != ts_game["ts_field"]
        ):

            changes.append(
                f"Field: "
                f"{ts_game['ts_field']} -> "
                f"{sssl_field}"
            )

        if changes:

            dashboard_rows.append({

                "status": "UPDATE",

                "team":
                    sssl_game.get(
                        "haysa_team",
                        ""
                    ),

                "opponent":
                    sssl_game.get(
                        "opponent_town",
                        ""
                    ),

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

                "ts_team":
                    ts_game[
                        "ts_team"
                    ],

                "ts_opponent":
                    ts_game[
                        "ts_opponent"
                    ],

                "ts_date":
                    ts_game[
                        "ts_date"
                    ],

                "ts_time":
                    ts_game[
                        "ts_time"
                    ],

                "ts_field":
                    ts_game[
                        "ts_field"
                    ],

                "ts_field_display":
                    ts_game[
                        "ts_field_display"
                    ],

                "action_required":
                    "; ".join(
                        changes
                    ),

                "event_id":
                    ts_game[
                        "calendar_event_id"
                    ]

            })

    #
    # TS Games Missing From SSSL
    #

    sssl_keys = {

        (

            game.get(
                "haysa_team",
                ""
            ),

            game.get(
                "opponent_town",
                ""
            )

        )

        for game in sssl_games
    }

    for ts_game in ts_games:

        key = (
            ts_game["ts_team"],
            ts_game["ts_opponent"]
        )

        if key not in sssl_keys:

            dashboard_rows.append({

                "status": "REVIEW",

                "team": "",

                "opponent": "",

                "sssl_date": "",

                "sssl_time": "",

                "sssl_field": "",

                "ts_team":
                    ts_game[
                        "ts_team"
                    ],

                "ts_opponent":
                    ts_game[
                        "ts_opponent"
                    ],

                "ts_date":
                    ts_game[
                        "ts_date"
                    ],

                "ts_time":
                    ts_game[
                        "ts_time"
                    ],

                "ts_field":
                    ts_game[
                        "ts_field"
                    ],

                "ts_field_display":
                    ts_game[
                        "ts_field_display"
                    ],

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
            )
        )
    )

    return dashboard_rows
