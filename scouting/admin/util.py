
from django.db import IntegrityError
from django.db.models import Q

import general.cloudinary
from form.models import Answer
from general.security import ret_message
import scouting
from scouting.models import (
    CompetitionLevel,
    Event,
    EventTeamInfo,
    Schedule,
    ScoutAuthGroup,
    FieldResponse,
    FieldSchedule,
    PitResponse,
    Season,
    Team,
    TeamNote,
    Match,
    UserInfo, FieldForm,
)
import scouting.util
import scouting.models
import alerts.util
from user.models import User
import user.util


def delete_event(event_id):
    e = Event.objects.get(event_id=event_id)

    if e.current == "y":
        raise Exception("Cannot delete current event.")

    teams_at_event = Team.objects.filter(event=e)
    for t in teams_at_event:
        t.event_set.remove(e)

    scout_fields = FieldResponse.objects.filter(event=e)
    for sf in scout_fields:
        scout_field_answers = Answer.objects.filter(response=sf.response)
        for sfa in scout_field_answers:
            sfa.delete()
        sf.delete()
        sf.response.delete()

    scout_pits = PitResponse.objects.filter(event=e)
    for sp in scout_pits:
        scout_pit_answers = Answer.objects.filter(response=sp.response)
        for spa in scout_pit_answers:
            spa.delete()

        for spi in sp.scoutpitimage_set.all():
            spi.delete()

        sp.delete()
        sp.response.delete()

    matches = Match.objects.filter(event=e)
    for m in matches:
        m.delete()

    scout_field_schedules = FieldSchedule.objects.filter(event=e)
    for sfs in scout_field_schedules:
        sfs.delete()

    schedules = Schedule.objects.filter(event=e)
    for s in schedules:
        s.delete()

    notes = TeamNote.objects.filter(event=e)
    for n in notes:
        n.delete()

    event_team_infos = EventTeamInfo.objects.filter(event=e)
    for eti in event_team_infos:
        eti.delete()

    e.delete()

    return ret_message("Successfully deleted event: " + e.event_nm)


def get_scout_auth_groups():
    sags = ScoutAuthGroup.objects.all().order_by("auth_group_id__name")

    groups = list(sag.auth_group_id for sag in sags)

    return groups


def add_season(year: str):
    try:
        season = Season.objects.get(season=year)
        raise Exception("Season already exists.")
    except Season.DoesNotExist as e:
        season = Season(season=year, current="n")
        season.save()

    return season


def save_season(data):
    if data.get("season_id", None) is not None:
        season = Season.objects.get(season_id=data["season_id"])
    else:
        season = Season(season=data["season"], current=data["current"]).save()

    return season


def delete_season(season_id):
    season = Season.objects.get(season_id=season_id)

    if season.current == "y":
        raise Exception("Cannot delete current season.")

    events = Event.objects.filter(season=season)
    for e in events:
        delete_event(e.event_id)

    scout_questions = scouting.models.Question.objects.filter(season=season)
    for sq in scout_questions:
        sq.delete()
        for qc in sq.question.condition_question_from.all():
            qc.delete()
        for qc in sq.question.condition_question_to.all():
            qc.delete()
        for qc in sq.question.questionaggregate_set.all():
            qc.delete()
        for qc in sq.question.questionoption_set.all():
            qc.delete()
        for qc in sq.question.questionanswer_set.all():
            qc.delete()
        sq.question.delete()  # this is the scout question which is an extension model for scouting questions

    season.delete()

    return ret_message("Successfully deleted season: " + season.season)


def save_event(data):
    if (data.get("event_id", None)) is not None:
        event = Event.objects.get(event_id=data["event_id"])
        event.season.season_id = data["season_id"]
        event.event_nm = data["event_nm"]
        event.date_st = data["date_st"]
        event.event_cd = data["event_cd"]
        event.event_url = data.get("event_url", None)
        event.address = data["address"]
        event.city = data["city"]
        event.state_prov = data["state_prov"]
        event.postal_code = data["postal_code"]
        event.location_name = data["location_name"]
        event.gmaps_url = data.get("gmaps_url", None)
        event.webcast_url = data.get("webcast_url", None)
        event.date_end = data["date_end"]
        event.timezone = data["timezone"]
        event.current = data["current"]
        event.competition_page_active = data["competition_page_active"]
        event.void_ind = data["void_ind"]
    else:
        event = Event(
            season_id=data["season_id"],
            event_nm=data["event_nm"],
            date_st=data["date_st"],
            event_cd=data["event_cd"],
            event_url=data.get("event_url", None),
            address=data["address"],
            city=data["city"],
            state_prov=data["state_prov"],
            postal_code=data["postal_code"],
            location_name=data["location_name"],
            gmaps_url=data.get("gmaps_url", None),
            webcast_url=data.get("webcast_url", None),
            date_end=data["date_end"],
            timezone=data["timezone"],
            current=data["current"],
            competition_page_active=data["competition_page_active"],
            void_ind=data["void_ind"],
        )

    event.save()
    return event


def link_team_to_Event(data):
    messages = ""

    for t in data.get("teams", []):
        try:  # TODO it doesn't throw an error, and re-linking many to many only keeps one entry in the table for the link
            if t.get("checked", False):
                team = Team.objects.get(team_no=t["team_no"], void_ind="n")
                e = Event.objects.get(event_id=data["event_id"], void_ind="n")
                team.event_set.add(e)
                messages += (
                    "(ADD) Added team: "
                    + str(t["team_no"])
                    + " "
                    + t["team_nm"]
                    + " to event: "
                    + e.event_cd
                    + "\n"
                )
        except IntegrityError:
            messages += (
                "(NO ADD) Team: "
                + str(t["team_no"])
                + " "
                + t["team_nm"]
                + " already at event: "
                + e.event_cd
                + "\n"
            )

    return messages


def remove_link_team_to_Event(data):
    messages = ""

    for t in data.get("teams", []):
        try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
            if t.get("checked", False):
                team = Team.objects.get(team_no=t["team_no"], void_ind="n")
                e = Event.objects.get(event_id=data["event_id"], void_ind="n")
                team.event_set.remove(e)
                messages += (
                    "(REMOVE) Removed team: "
                    + str(t["team_no"])
                    + " "
                    + t["team_nm"]
                    + " from event: "
                    + e.event_cd
                    + "\n"
                )
        except IntegrityError:
            messages += (
                "(NO REMOVE) Team: "
                + str(t["team_no"])
                + " "
                + t["team_nm"]
                + " from event: "
                + e.event_cd
                + "\n"
            )

    return messages


def save_scout_schedule(data):
    if data["end_time"] <= data["st_time"]:
        raise Exception("End time can't come before start.")

    if data.get("scout_field_sch_id", None) is None:
        sfs = FieldSchedule(
            event_id=data["event_id"],
            st_time=data["st_time"],
            end_time=data["end_time"],
            red_one_id=data.get("red_one_id", None),
            red_two_id=data.get("red_two_id", None),
            red_three_id=data.get("red_three_id", None),
            blue_one_id=data.get("blue_one_id", None),
            blue_two_id=data.get("blue_two_id", None),
            blue_three_id=data.get("blue_three_id", None),
            void_ind=data["void_ind"],
        )
    else:
        sfs = FieldSchedule.objects.get(
            scout_field_sch_id=data["scout_field_sch_id"]
        )
        sfs.red_one_id = data.get("red_one_id", None)
        sfs.red_two_id = data.get("red_two_id", None)
        sfs.red_three_id = data.get("red_three_id", None)
        sfs.blue_one_id = data.get("blue_one_id", None)
        sfs.blue_two_id = data.get("blue_two_id", None)
        sfs.blue_three_id = data.get("blue_three_id", None)
        sfs.st_time = data["st_time"]
        sfs.end_time = data["end_time"]
        sfs.void_ind = data["void_ind"]

    sfs.save()
    return sfs


def save_schedule(data):
    if data["end_time"] <= data["st_time"]:
        raise Exception("End time can't come before start.")

    if data.get("sch_id", None) is None:
        event = scouting.util.get_current_event()

        s = Schedule(
            event=event,
            st_time=data["st_time"],
            end_time=data["end_time"],
            user_id=data.get("user", None),
            sch_typ_id=data.get("sch_typ", None),
            void_ind=data["void_ind"],
        )
    else:
        s = Schedule.objects.get(sch_id=data["sch_id"])
        s.user.pk = data.get("user", None)
        s.sch_typ.sch_typ = data.get("sch_typ", None)
        s.st_time = data["st_time"]
        s.end_time = data["end_time"]
        s.void_ind = data["void_ind"]

    s.save()
    return s


def notify_user(id):
    sch = Schedule.objects.get(sch_id=id)
    message = alerts.util.stage_schedule_alert(sch)
    alerts.util.send_alerts()
    sch.notified = True
    sch.save()

    return message


def notify_users(id):
    event = Event.objects.get(Q(current="y") & Q(void_ind="n"))
    sfs = FieldSchedule.objects.get(scout_field_sch_id=id)
    message = alerts.util.stage_field_schedule_alerts(-1, [sfs], event)
    alerts.util.send_alerts()
    return message


def get_scouting_user_info():
    user_results = []
    users = user.util.get_users(1, 0)
    for u in users:
        try:
            user_info = u.scouting_user_info.get(void_ind="n")
        except UserInfo.DoesNotExist:
            user_info = {}

        user_results.append(
            {
                "user": u,
                "user_info": user_info,
            }
        )

    return user_results


def toggle_user_under_review(user_id):
    try:
        ui = UserInfo.objects.get(Q(user__id=user_id) & Q(void_ind="n"))
    except UserInfo.DoesNotExist:
        ui = UserInfo(
            user=User.objects.get(id=user_id),
            under_review=False,
        )

    ui.under_review = not ui.under_review

    ui.save()


def void_field_response(id):
    sf = FieldResponse.objects.get(scout_field_id=id)
    sf.void_ind = "y"
    sf.save()
    return sf


def void_scout_pit_response(id):
    sp = PitResponse.objects.get(scout_pit_id=id)

    sp.response.void_ind = "y"
    sp.void_ind = "y"
    sp.save()
    return sp


def save_field_form(field_form):
    if field_form.get("id", None) is not None:
        ff = FieldForm.objects.get(id=field_form["id"])
    else:
        ff = FieldForm()
        ff.season = scouting.util.get_current_season()

    img = None
    if field_form.get("img", None) is not None:
        img = general.cloudinary.upload_image(field_form["img"], ff.img_id)

    inv_img = None
    if field_form.get("inv_img", None) is not None:
        inv_img = general.cloudinary.upload_image(field_form["inv_img"], ff.inv_img_id)

    full_img = None
    if field_form.get("full_img", None) is not None:
        full_img = general.cloudinary.upload_image(field_form["full_img"], ff.full_img_id)

    if img is not None:
        ff.img_id = img["public_id"]
        ff.img_ver = img["version"]

    if inv_img is not None:
        ff.inv_img_id = inv_img["public_id"]
        ff.inv_img_ver = inv_img["version"]

    if full_img is not None:
        ff.full_img_id = full_img["public_id"]
        ff.full_img_ver = full_img["version"]

    ff.save()