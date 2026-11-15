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


def parse_event_summary(text):

    if " vs. " not in text:
        return "", ""

    team, opponent = text.split(
        " vs. ",
        1
    )

    return (
        team.strip(),
        opponent.strip()
    )


def generate_dashboard(
    sssl_games,
    events
):

    dashboard_rows = []

    #
    # Active TS game events only
    #

    ts_games = []

    for event in events:

        if (
            event.get("type") == "game"
            and event.get("status") == "active"
        ):

            ts_games.append(event)

    #
    # Build lookup
    #

    ts_lookup = {}

    for event in ts_games:

        team, opponent = parse_event_summary(
            event.get(
                "team",
                ""
            )
        )

        key = (
            team,
            opponent
        )

        ts_lookup[key] = event

    #
    # Compare SSSL -> TS
    #

    for game in sssl_games:

        key = (
            game.get(
                "haysa_team",
                ""
            ),
            game.get(
                "opponent_town",
                ""
            )
        )

        ts_game = ts_lookup.get(key)

        #
        # Missing from TS
        #

        if not ts_game:

            dashboard_rows.append({

                "status": "CREATE",

                "team":
                    game.get(
                        "haysa_team",
                        ""
                    ),

                "opponent":
                    game.get(
                        "opponent_town",
                        ""
                    ),

                "sssl_date":
                    game.get(
                        "date",
                        ""
                    ),

                "sssl_time":
                    game.get(
                        "start_time",
                        ""
                    ),

                "sssl_field":
                    game.get(
                        "ts_field_code",
                        ""
                    ),

                "ts_date": "",

                "ts_time": "",

                "ts_field": "",

                "action_required":
                    "Create TeamSideline game",

                "event_id": ""

            })

            continue

        changes = []

        sssl_date = normalize_date(
            game.get(
                "date",
                ""
            )
        )

        ts_date = normalize_date(
            ts_game.get(
                "date",
                ""
            )
        )

        if (
            sssl_date
            and ts_date
            and sssl_date != ts_date
        ):

            changes.append(
                f"Date: {ts_date} -> {sssl_date}"
            )

        sssl_time = normalize_time(
            game.get(
                "start_time",
                ""
            )
        )

        ts_time = normalize_time(
            ts_game.get(
                "start_time",
                ""
            )
        )

        if (
            sssl_time
            and ts_time
            and sssl_time != ts_time
        ):

            changes.append(
                f"Time: {ts_time} -> {sssl_time}"
            )

        sssl_field = (
            game.get(
                "ts_field_code",
                ""
            )
            .strip()
        )

        ts_field = (
            ts_game.get(
                "field",
                ""
            )
            .strip()
        )

        if (
            sssl_field
            and ts_field
            and sssl_field != ts_field
        ):

            changes.append(
                f"Field: {ts_field} -> {sssl_field}"
            )

        if changes:

            dashboard_rows.append({

                "status": "UPDATE",

                "team":
                    game.get(
                        "haysa_team",
                        ""
                    ),

                "opponent":
                    game.get(
                        "opponent_town",
                        ""
                    ),

                "sssl_date":
                    game.get(
                        "date",
                        ""
                    ),

                "sssl_time":
                    game.get(
                        "start_time",
                        ""
                    ),

                "sssl_field":
                    game.get(
                        "ts_field_code",
                        ""
                    ),

                "ts_date":
                    ts_game.get(
                        "date",
                        ""
                    ),

                "ts_time":
                    ts_game.get(
                        "start_time",
                        ""
                    ),

                "ts_field":
                    ts_game.get(
                        "field",
                        ""
                    ),

                "action_required":
                    "; ".join(changes),

                "event_id":
                    ts_game.get(
                        "calendar_event_id",
                        ""
                    )

            })

    #
    # TS games not found in SSSL
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

    for event in ts_games:

        team, opponent = parse_event_summary(
            event.get(
                "team",
                ""
            )
        )

        key = (
            team,
            opponent
        )

        if key not in sssl_keys:

            dashboard_rows.append({

                "status": "REVIEW",

                "team": team,

                "opponent": opponent,

                "sssl_date": "",

                "sssl_time": "",

                "sssl_field": "",

                "ts_date":
                    event.get(
                        "date",
                        ""
                    ),

                "ts_time":
                    event.get(
                        "start_time",
                        ""
                    ),

                "ts_field":
                    event.get(
                        "field",
                        ""
                    ),

                "action_required":
                    "Exists in TeamSideline but not in SSSL",

                "event_id":
                    event.get(
                        "calendar_event_id",
                        ""
                    )

            })

    dashboard_rows.sort(
        key=lambda x: (
            x["status"],
            x["team"]
        )
    )

    return dashboard_rows
