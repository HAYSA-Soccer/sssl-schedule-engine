def parse_event_summary(summary):

    if " vs. " not in summary:
        return "", ""

    team, opponent = summary.split(
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
    # Only active TS games
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
            event.get("summary", "")
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
        # Missing in TS
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

                "action_required":
                    f"Create game on "
                    f"{game.get('date')} "
                    f"at "
                    f"{game.get('start_time')}",

                "event_id": ""

            })

            continue

        changes = []

        #
        # Date
        #

        sssl_date = game.get(
            "date",
            ""
        )

        ts_date = ts_game.get(
            "date",
            ""
        )

        #
        # Time
        #

        sssl_time = game.get(
            "start_time",
            ""
        )

        ts_time = ts_game.get(
            "start_time",
            ""
        )

        #
        # Field
        #

        sssl_field = game.get(
            "ts_field_code",
            ""
        )

        ts_field = ts_game.get(
            "field",
            ""
        )

        if sssl_date and ts_date:

            if str(sssl_date) != str(ts_date):

                changes.append(
                    f"Change date "
                    f"from {ts_date} "
                    f"to {sssl_date}"
                )

        if sssl_time and ts_time:

            if str(sssl_time) != str(ts_time):

                changes.append(
                    f"Change time "
                    f"from {ts_time} "
                    f"to {sssl_time}"
                )

        if (
            sssl_field
            and ts_field
            and sssl_field != ts_field
        ):

            changes.append(
                f"Change field "
                f"from {ts_field} "
                f"to {sssl_field}"
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

                "action_required":
                    ". ".join(changes),

                "event_id":
                    ts_game.get(
                        "calendar_event_id",
                        ""
                    )

            })

    #
    # Summary row
    #

    dashboard_rows.sort(
        key=lambda x: (
            x["status"],
            x["team"]
        )
    )

    return dashboard_rows
