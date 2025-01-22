import pytz
from django.db.models import Q

import general.cloudinary
import scouting
import scouting.util
from general.security import ret_message
from scouting.models import Event, Team, TeamNote, MatchStrategy, AllianceSelection
from user.models import User


def get_team_notes(team_no: int = None, event: Event = None):
    q_event = Q()
    q_team = Q()

    if team_no is not None:
        q_team = Q(team_no=Team.objects.get(Q(void_ind="n") & Q(team_no=team_no)))

    if event is not None:
        q_event = Q(event=event)

    notes = TeamNote.objects.filter(
        Q(void_ind="n") & q_team & q_event
    ).order_by("-time")

    return [parse_team_note(n) for n in notes]


def parse_team_note(n: TeamNote):
    return {
        "team_note_id": n.team_note_id,
        "team_id": n.team_no.team_no,
        "match_id": n.match.match_id if n.match else None,
        "note": n.note,
        "time": n.time,
        "user": n.user
    }


def save_note(data, user: User):
    current_event = scouting.util.get_current_event()

    note = TeamNote(
        event=current_event,
        team_no_id=data["team_id"],
        match_id=data.get("match_id", None),
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

    match_strategies = MatchStrategy.objects.filter(q_match_id & q_event & Q(void_ind="n")).order_by("-time")

    parsed_match_strategies = []
    for ms in match_strategies:
        parsed_match_strategies.append({
            "id": ms.id,
            "match": scouting.util.parse_match(ms.match),
            "user": ms.user,
            "strategy": ms.strategy,
            "img_url": general.cloudinary.build_image_url(ms.img_id, ms.img_ver),
            "time": ms.time,
            "display_value": f"{ms.user.get_full_name()} {ms.time.astimezone(pytz.timezone('America/New_York' if event is None else event.timezone)).strftime('%m/%d/%Y, %I:%M%p')}"

        })

    return parsed_match_strategies


def save_match_strategy(data, img = None):
    if data.get("id", None) is not None:
        match_strategy = MatchStrategy.objects.get(id=data["id"])
    else:
        match_strategy = MatchStrategy()

    match_strategy.match_id = data["match_id"]
    match_strategy.user_id = data["user_id"]
    match_strategy.strategy = data["strategy"]

    if img is not None:
        img = general.cloudinary.upload_image(img, match_strategy.img_id)

    if img is not None:
        match_strategy.img_id = img["public_id"]
        match_strategy.img_ver = img["version"]

    match_strategy.save()


def get_alliance_selections():
    selections = AllianceSelection.objects.filter(
        Q(event=scouting.util.get_current_event()) & Q(void_ind="n")).order_by("order")

    parsed = []
    for selection in selections:
        parsed.append({
            "id": selection.id,
            "event": selection.event,
            "team": selection.team,
            "note": selection.note,
            "order": selection.order
        })

    return selections


def save_alliance_selections(data):
    for d in data:
        if d.get("id") is not None:
            selection = AllianceSelection.objects.get(id=d["id"])
        else:
            selection = AllianceSelection()

        selection.event_id = d["event"]["event_id"]
        selection.team_id = d["team"]["team_no"]
        selection.note = d["note"]
        selection.order = d["order"]

        selection.save()
