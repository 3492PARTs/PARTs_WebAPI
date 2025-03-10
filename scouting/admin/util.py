from django.db import IntegrityError
from django.db.models import Q

import general.cloudinary
import general.util
import tba.util
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
    UserInfo,
    FieldForm,
)
import scouting.util
import scouting.models
import alerts.util
from user.models import User
import user.util


def set_current_season_event(season_id, event_id, competition_page_active):
    msg = ""

    Season.objects.filter(current="y").update(current="n")
    season = Season.objects.get(id=season_id)
    season.current = "y"
    season.save()
    msg = "Successfully set the season to: " + season.season

    if event_id is not None:
        Event.objects.filter(current="y").update(
            current="n", competition_page_active="n"
        )
        event = Event.objects.get(id=event_id)
        event.current = "y"
        event.competition_page_active = competition_page_active
        event.save()
        msg += "\nSuccessfully set the event to: " + event.event_nm

        msg += f"\nCompetition page {'active' if competition_page_active == 'y' else 'inactive'}"

    return msg


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
    sags = ScoutAuthGroup.objects.all().order_by("group__name")

    groups = list(sag.group for sag in sags)

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
        delete_event(e.id)

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
        event.season.id = data["season_id"]
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


def save_match(data):
    if (data.get("match_key", None)) is not None and len(data["match_key"]) > 0:
        match = Match.objects.get(match_key=data["match_key"])
    else:
        match = Match(
            match_key=f"{data['event']['event_cd']}_{data['comp_level']['comp_lvl_typ']}{data['match_number']}"
        )
        match.event_id = data["event"]["id"]

    match.match_number = data["match_number"]
    match.red_one_id = data["red_one_id"]
    match.red_two_id = data["red_two_id"]
    match.red_three_id = data["red_three_id"]
    match.blue_one_id = data["blue_one_id"]
    match.blue_two_id = data["blue_two_id"]
    match.blue_three_id = data["blue_three_id"]
    match.time = data["time"]
    match.comp_level_id = data["comp_level"]["comp_lvl_typ"]

    match.save()
    return match


def link_team_to_event(data):
    messages = ""

    for t in data.get("teams", []):
        try:  # TODO it doesn't throw an error, and re-linking many to many only keeps one entry in the table for the link
            if t.get("checked", False):
                team = Team.objects.get(team_no=t["team_no"], void_ind="n")
                e = Event.objects.get(id=data["event_id"], void_ind="n")
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


def remove_link_team_to_event(data):
    messages = ""

    for t in data.get("teams", []):
        try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
            if t.get("checked", False):
                team = Team.objects.get(team_no=t["team_no"], void_ind="n")
                e = Event.objects.get(id=data["id"], void_ind="n")
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

    if data.get("id", None) is None:
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
        sfs = FieldSchedule.objects.get(id=data["id"])
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

    if data.get("id", None) is None:
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
        s = Schedule.objects.get(id=data["id"])
        s.user.pk = data.get("user", None)
        s.sch_typ.sch_typ = data.get("sch_typ", None)
        s.st_time = data["st_time"]
        s.end_time = data["end_time"]
        s.void_ind = data["void_ind"]

    s.save()
    return s


def notify_user(id):
    sch = Schedule.objects.get(id=id)
    message = alerts.util.stage_schedule_alert(sch)
    alerts.util.send_alerts()
    sch.notified = True
    sch.save()

    return message


def notify_users(id):
    event = Event.objects.get(Q(current="y") & Q(void_ind="n"))
    sfs = FieldSchedule.objects.get(id=id)
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
            user_info = UserInfo(user=u)
            user_info.save()

        user_results.append(user_info)

    return user_results


def save_scouting_user_info(data):
    if data.get("id", None) is not None:
        user_info = UserInfo.objects.get(id=data["id"])
    else:
        user_info = UserInfo(user_id=data["user"]["id"])

    user_info.group_leader = data["group_leader"]
    user_info.under_review = data["under_review"]
    user_info.eliminate_results = data["eliminate_results"]

    user_info.save()


def void_field_response(id):
    sf = FieldResponse.objects.get(id=id)
    sf.void_ind = "y"
    sf.save()
    return sf


def void_scout_pit_response(id):
    sp = PitResponse.objects.get(id=id)

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
        full_img = general.cloudinary.upload_image(
            field_form["full_img"], ff.full_img_id
        )

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


def foo():
    team_3492 = Team.objects.get(team_no=3492)

    current_season = scouting.util.get_current_season()

    our_events = team_3492.event_set.filter(
        Q(void_ind="n") & Q(season=current_season)
    ).order_by("date_end")

    event_cds = [event.event_cd for event in our_events]

    # csv = "team,sharing event,other events,match data\n"
    csv = ""

    highest_event_date = our_events[len(our_events) - 1].date_end

    for event in our_events:
        teams = event.teams.filter(~Q(team_no=3492)).order_by("team_no")
        for team in teams:
            # print(team)
            csv += f"Team: {team.team_no}\n"

            team_events = tba.util.get_events_for_team(team, current_season, event_cds)

            sharing = ""
            other = ""

            for team_event in team_events:
                csv_matches = ""
                first_run = True

                if team_event["event_cd"] in event_cds:
                    # print(f"same as us {team_event['event_cd']}")
                    csv += f"Sharing,{[event.event_nm for event in our_events if event.event_cd == team_event['event_cd']][0]}\n"
                    sharing += f"{[event.event_nm for event in our_events if event.event_cd == team_event['event_cd']][0]}, "
                else:
                    # print(f"Different {team_event['event_nm']}")
                    csv += f"Other,{team_event['event_nm']},{general.util.date_time_to_mdyhm(team_event['date_st'], team_event.get('timezone', 'America/New_York'))},{general.util.date_time_to_mdyhm(team_event['date_end'], team_event.get('timezone', 'America/New_York'))}\n"

                    if team_event["date_end"] < highest_event_date:
                        other += f"{team_event['event_nm']}, "

                        matches = tba.util.get_matches_for_team_event(
                            team.team_no, team_event["event_cd"]
                        )

                        if len(matches) > 0:
                            csv += f"Match Data\n"

                        for match in matches:
                            csv_match = ""
                            csv_match += f"Match {match['match_number']},https://www.thebluealliance.com/match/{match['key']},,,,,\n"
                            csv_match += f"Teams,,,Score,,,\n"
                            csv_match += f"{tba.util.replace_frc_in_str(match['alliances']['red']['team_keys'][0])},{tba.util.replace_frc_in_str(match['alliances']['red']['team_keys'][1])},{tba.util.replace_frc_in_str(match['alliances']['red']['team_keys'][2])},{match['alliances']['red']['score']},,,\n"
                            csv_match += f"{tba.util.replace_frc_in_str(match['alliances']['blue']['team_keys'][0])},{tba.util.replace_frc_in_str(match['alliances']['blue']['team_keys'][1])},{tba.util.replace_frc_in_str(match['alliances']['blue']['team_keys'][2])},{match['alliances']['blue']['score']},,,\n"

                            if match["score_breakdown"] is not None:
                                csv_match += "Detailed Results,,,,,,\n"
                                csv_match += f"{match['score_breakdown']['red']['autoLineRobot1']},{match['score_breakdown']['red']['autoLineRobot2']},{match['score_breakdown']['red']['autoLineRobot3']},Auto Leave,{match['score_breakdown']['blue']['autoLineRobot1']},{match['score_breakdown']['blue']['autoLineRobot2']},{match['score_breakdown']['blue']['autoLineRobot3']}\n"

                                # auto
                                csv_match += f"L4,{match['score_breakdown']['red']['autoReef']['tba_topRowCount']},,Auto Coral Count,,{match['score_breakdown']['blue']['autoReef']['tba_topRowCount']},L4\n"
                                csv_match += f"L3,{match['score_breakdown']['red']['autoReef']['tba_midRowCount']},,Auto Coral Count,,{match['score_breakdown']['blue']['autoReef']['tba_midRowCount']},L3\n"
                                csv_match += f"L2,{match['score_breakdown']['red']['autoReef']['tba_topRowCount']},,Auto Coral Count,,{match['score_breakdown']['blue']['autoReef']['tba_topRowCount']},L2\n"
                                csv_match += f"L1,{match['score_breakdown']['red']['autoReef']['trough']},,Auto Coral Count,,{match['score_breakdown']['blue']['autoReef']['trough']},L1\n"
                                csv_match += f",{match['score_breakdown']['red']['autoCoralPoints']},,Auto Coral Points,,{match['score_breakdown']['blue']['autoCoralPoints']},\n"
                                csv_match += f",{match['score_breakdown']['red']['autoPoints']},,Total Auto,,{match['score_breakdown']['blue']['autoPoints']},\n"

                                # tele
                                csv_match += f"L4,{match['score_breakdown']['red']['teleopReef']['tba_topRowCount']},,Teleop Coral Count,,{match['score_breakdown']['blue']['teleopReef']['tba_topRowCount']},L4\n"
                                csv_match += f"L3,{match['score_breakdown']['red']['teleopReef']['tba_midRowCount']},,Teleop Coral Count,,{match['score_breakdown']['blue']['teleopReef']['tba_midRowCount']},L3\n"
                                csv_match += f"L2,{match['score_breakdown']['red']['teleopReef']['tba_topRowCount']},,Teleop Coral Count,,{match['score_breakdown']['blue']['teleopReef']['tba_topRowCount']},L2\n"
                                csv_match += f"L1,{match['score_breakdown']['red']['teleopReef']['trough']},,Teleop Coral Count,,{match['score_breakdown']['blue']['teleopReef']['trough']},L1\n"
                                csv_match += f",{match['score_breakdown']['red']['teleopCoralPoints']},,Teleop Coral Points,,{match['score_breakdown']['blue']['teleopCoralPoints']},\n"

                                csv_match += f",{match['score_breakdown']['red']['wallAlgaeCount']},,Processor Algae Count,,{match['score_breakdown']['blue']['wallAlgaeCount']},\n"
                                csv_match += f",{match['score_breakdown']['red']['netAlgaeCount']},,Net Algae Count,,{match['score_breakdown']['blue']['netAlgaeCount']},\n"
                                csv_match += f",{match['score_breakdown']['red']['algaePoints']},,Algae Points,,{match['score_breakdown']['blue']['algaePoints']},\n"

                                # endgame
                                csv_match += f"{tba.util.replace_frc_in_str(match['alliances']['red']['team_keys'][0])},{match['score_breakdown']['red']['endGameRobot1']},,Robot 1 Endgame,,{match['score_breakdown']['blue']['endGameRobot1']},{tba.util.replace_frc_in_str(match['alliances']['blue']['team_keys'][0])}\n"
                                csv_match += f"{tba.util.replace_frc_in_str(match['alliances']['red']['team_keys'][1])},{match['score_breakdown']['red']['endGameRobot2']},,Robot 2 Endgame,,{match['score_breakdown']['blue']['endGameRobot2']},{tba.util.replace_frc_in_str(match['alliances']['blue']['team_keys'][1])}\n"
                                csv_match += f"{tba.util.replace_frc_in_str(match['alliances']['red']['team_keys'][2])},{match['score_breakdown']['red']['endGameRobot3']},,Robot 3 Endgame,,{match['score_breakdown']['blue']['endGameRobot3']},{tba.util.replace_frc_in_str(match['alliances']['blue']['team_keys'][2])}\n"
                                csv_match += f",{match['score_breakdown']['red']['endGameBargePoints']},,Barge Points,,{match['score_breakdown']['blue']['endGameBargePoints']},\n"

                                csv_match += f",{match['score_breakdown']['red']['teleopPoints']},,Total Teleop,,{match['score_breakdown']['blue']['teleopPoints']},\n"

                                csv_match += f",{match['score_breakdown']['red']['coopertitionCriteriaMet']},,Coopertition Criteria Met,,{match['score_breakdown']['blue']['coopertitionCriteriaMet']},\n"
                                csv_match += f",{match['score_breakdown']['red']['autoBonusAchieved']},,Auto Bonus,,{match['score_breakdown']['blue']['autoBonusAchieved']},\n"
                                csv_match += f",{match['score_breakdown']['red']['coralBonusAchieved']},,Coral Bonus,,{match['score_breakdown']['blue']['coralBonusAchieved']},\n"
                                csv_match += f",{match['score_breakdown']['red']['bargeBonusAchieved']},,Barge Bonus,,{match['score_breakdown']['blue']['bargeBonusAchieved']},\n"
                                csv_match += f",{match['score_breakdown']['red']['foulCount']}/{match['score_breakdown']['red']['techFoulCount']},,Fouls / Tech Fouls,,{match['score_breakdown']['blue']['foulCount']}/{match['score_breakdown']['red']['techFoulCount']},\n"
                                csv_match += f",{match['score_breakdown']['red']['foulPoints']},,Foul Points,,{match['score_breakdown']['blue']['foulPoints']},\n"
                                csv_match += f",{match['score_breakdown']['red']['adjustPoints']},,Adjustments,,{match['score_breakdown']['blue']['adjustPoints']},\n"
                                csv_match += f",{match['score_breakdown']['red']['totalPoints']},,Total Score,,{match['score_breakdown']['blue']['totalPoints']},\n"
                                csv_match += f",{match['score_breakdown']['red']['rp']},,Ranking Points,,{match['score_breakdown']['blue']['rp']},\n"

                            if first_run:
                                csv_matches = csv_match
                                first_run = False
                            else:
                                # Concatenate lines horizontally
                                csv_matches = "\n".join(
                                    [
                                        ",,".join(elem)
                                        for elem in zip(
                                            csv_matches.split("\n"),
                                            csv_match.split("\n"),
                                        )
                                    ]
                                )

                        csv += f"{csv_matches}\n"
        csv += "\n"
    return csv
