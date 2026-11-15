import re


def parse_event_summary(summary):
    """
    Convert:

    '7/8 Boys Travel (Mills) vs. Easton'

    into:

    ('7/8 Boys Travel (Mills)', 'Easton')
    """

    if " vs. " not in summary:
        return "", ""

    team, opponent = summary.split(" vs. ", 1)

    return team.strip(), opponent.strip()


def generate_dashboard(sssl_games, events):

    dashboard_rows = []

    #
    # TeamSideline games only
    #

    ts_games = [
        event
        for event in events
        if event.get("type") == "game"
        and event.get("status") == "active"
    ]

    #
    # Build TS lookup
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

    matched_keys = set()

    #
    # Compare SSSL against TS
    #

    for game in sssl_games:

        key = (
            game.get("haysa_team", ""),
            game.get("opponent_town", "")
        )

        ts_game = ts_lookup.get(key)

        #
        # Missing from TS
        #

        if not ts_game:

            dashboard_rows.append({
                "status": "CREATE",
                "team": game.get("haysa_team", ""),
                "opponent": game.get("opponent_town", ""),
                "action_required":
                    f"Create TeamSideline game on "
                    f"{game.get('date')} "
                    f"at {game.get('start_time')}.",
                "event_id": ""
            })

            continue

        matched_keys.add(key)

        changes = []

        #
        # Date
        #

        sssl_date = game.get("date", "").strip()
        ts_date = ts_game.get("date", "").strip()

        if sssl_date != ts_date:

            changes.append(
                f"date from {ts_date} to {sssl_date}"
            )

        #
        # Time
        #

        sssl_time = game.get("start_time", "").strip()
        ts_time = ts_game.get("start_time", "").strip()

        if sssl_time != ts_time:

            changes.append(
                f"time from {ts_time} to {sssl_time}"
            )

        #
        # Field
        #

        sssl_field = game.get(
            "ts_field_code",
            ""
        ).strip()

        ts_field = ts_game.get(
            "field",
            ""
        ).strip()

        if (
            sssl_field
            and ts_field
            and sssl_field != ts_field
        ):

            changes.append(
                f"field from {ts_field} to {sssl_field}"
            )

        #
        # Update needed
        #

        if changes:

            dashboard_rows.append({
                "status": "UPDATE",
                "team": game.get("haysa_team", ""),
                "opponent": game.get("opponent_town", ""),
                "action_required":
                    "Change " + ", ".join(changes) + ".",
                "event_id":
                    ts_game.get(
                        "calendar_event_id",
                        ""
                    )
            })

    #
    # Find games in TS
    # but not in SSSL
    #

    sssl_keys = {
        (
            game.get("haysa_team", ""),
            game.get("opponent_town", "")
        )
        for game in sssl_games
    }

    for event in ts_games:

        team, opponent = parse_event_summary(
            event.get("summary", "")
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
                "action_required":
                    "Game exists in TeamSideline but "
                    "not in SSSL. Review before deleting.",
                "event_id":
                    event.get(
                        "calendar_event_id",
                        ""
                    )
            })

    return dashboard_rows
