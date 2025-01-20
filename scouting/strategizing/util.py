from django.db.models import Q

from general.security import ret_message
import scouting
from scouting.models import Event, Team, TeamNotes, MatchStrategy
import scouting.util
from user.models import User


def get_team_notes(team_no: int = None, event: Event = None):
    q_event = Q()
    q_team = Q()

    if team_no is not None:
        q_team = Q(team_no=Team.objects.get(Q(void_ind="n") & Q(team_no=team_no)))

    if event is not None:
        q_event = Q(event=event)

    notes = TeamNotes.objects.filter(
        Q(void_ind="n") & q_team & q_event
    ).order_by("-time")

    return notes


def get_parsed_team_noes(team_no: int):
    notes = get_team_notes(team_no)

    parsed_notes = []
    for n in notes:
        parsed_notes.append(
            {
                "team_note_id": n.team_note_id,
                "team_no": n.team_no.team_no,
                "match_id": n.match.match_id if n.match else None,
                "note": n.note,
                "time": n.time,
            }
        )

    return parsed_notes


def save_note(data, user: User):
    current_event = scouting.util.get_current_event()

    note = TeamNotes(
        event=current_event,
        team_no_id=data["team_no"],
        match_id=data.get("match", None),
        user=user,
        note=data["note"],
    )

    note.save()

    return ret_message("Note saved successfully")


def get_match_strategies(match_id: int = None, event: Event = None):
    q_match_id = Q()
    q_event = Q()

    if match_id is not None:
        q_match_id = Q(id=match_id)

    if event is not None:
        q_event = Q(match__event=event)

    match_strategies = MatchStrategy.objects.filter(q_match_id & q_event & Q(void_ind="n"))

    parsed_match_strategies = []
    for ms in match_strategies:
        parsed_match_strategies.append({
            "id": ms.id,
            "match": scouting.util.parse_match(ms.match),
            "user": ms.user,
            "strategy": ms.strategy,
        })

    return parsed_match_strategies

def save_match_strategy(data) :
    if data.get("id", None) is not None:
        match_strategy = MatchStrategy.objects.get(id=data["id"])
    else:
        match_strategy = MatchStrategy()

    match_strategy.match_id = data["match"]["match_id"]
    match_strategy.user_id = data["user"]["id"]
    match_strategy.strategy = data["strategy"]

    match_strategy.save()