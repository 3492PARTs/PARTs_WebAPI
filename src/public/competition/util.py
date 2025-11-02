from typing import Any
from django.db.models import Q

from scouting.models import Event, Match, Team
import scouting.util


def get_competition_information() -> dict[str, Any]:
    """
    Get the current competition event information and team 3492's match schedule.
    
    Returns:
        Dictionary containing 'event' (Event object) and 'matches' (list of parsed match dicts)
        for the current active competition
    """
    event = Event.objects.get(
        Q(current="y") & Q(competition_page_active="y") & Q(void_ind="n")
    )
    team3492 = Team.objects.get(team_no=3492)

    matches = Match.objects.filter(
        Q(event=event)
        & Q(void_ind="n")
        & Q(
            Q(red_one=team3492)
            | Q(red_two=team3492)
            | Q(red_three=team3492)
            | Q(blue_one=team3492)
            | Q(blue_two=team3492)
            | Q(blue_three=team3492)
        )
    ).order_by("comp_level__comp_lvl_order", "match_number")

    matches = list(scouting.util.parse_match(m) for m in matches)

    return {"event": event, "matches": matches}
