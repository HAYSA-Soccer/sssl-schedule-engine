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

    matchup = str(
        event.get(
            "team",
            ""
        )
    ).strip()

    separators = [
        " vs. ",
        " vs ",
        " VS ",
        " v. ",
        " v "
    ]

    ts_team = ""
    ts_opponent = ""

    for separator in separators:

        if separator in matchup:

            ts_team, ts_opponent = matchup.split(
                separator,
                1
            )

            break

    return {

        "raw_matchup":
            matchup,

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
            str(
                event.get(
                    "field",
                    ""
                )
            ).strip(),

        "ts_field_display":
            str(
                event.get(
                    "field_display",
                    ""
                )
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
    # Active TS game events
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
    # Build lookup
    #

    ts_lookup = {}

    for game in ts_games:

        key = (

            game["ts_team"].strip(),

            game["ts_opponent"].strip(),

            game["ts_date"]

        )

        ts_lookup[key] = game

    #
    # Compare SSSL -> TS
    #

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

        #
        # Missing from TS
        #

        if not ts_game:

            dashboard_rows.append({

                "status": "CREATE",

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

                "raw_matchup": "",
                
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

        if (
            sssl_date
            and ts_game["ts_date"]
            and sssl_date != ts_game["ts_date"]
        ):

            changes.append(
                f"Date: {ts_game['ts_date']} -> {sssl_date}"
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
                f"Time: {ts_game['ts_time']} -> {sssl_time}"
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
                f"Field: {ts_game['ts_field']} -> {sssl_field}"
            )

        if changes:

            dashboard_rows.append({

                "status": "UPDATE",

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

    #
    # TS games missing from SSSL
    #

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

                "status": "REVIEW",

                "team": "",

                "opponent": "",

                "sssl_date": "",

                "sssl_time": "",

                "sssl_field": "",

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
