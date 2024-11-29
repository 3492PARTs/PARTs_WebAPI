from django.db.models import Q

from general.security import ret_message
import scouting
from scouting.models import Event, Team, TeamNotes
import scouting.util
from user.models import User


def get_team_notes(team_no: int):
    current_event = scouting.util.get_current_event()

    team = Q()

    if team_no is not None:
        team = Q(team_no=Team.objects.get(Q(void_ind="n") & Q(team_no=team_no)))

    notes = TeamNotes.objects.filter(
        Q(void_ind="n") & team & Q(event=current_event)
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
