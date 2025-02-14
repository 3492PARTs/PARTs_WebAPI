from django.db.models import Q

import general.cloudinary
from form.models import Answer
from general.security import ret_message
import scouting
import form
from scouting.models import EventTeamInfo, PitResponse, PitImage, Team


def get_responses(team=None):
    current_season = scouting.util.get_current_season()

    current_event = scouting.util.get_current_event()

    teamCondition = Q()
    if team is not None:
        teamCondition = Q(team_no=team)

    teams = (
        Team.objects.prefetch_related("eventteaminfo_set")
        .filter(teamCondition & Q(event=current_event))
        .order_by("team_no")
    )

    questions = form.util.get_questions("pit")

    results = []
    for team in teams:
        try:
            pit_response = PitResponse.objects.prefetch_related("pitimage_set").get(
                Q(team=team)
                & Q(event=current_event)
                & Q(void_ind="n")
                & Q(response__void_ind="n")
            )
        except PitResponse.DoesNotExist as e:
            pit_response = None

        if pit_response is not None:
            pit_images = pit_response.pitimage_set.filter(Q(void_ind="n")).order_by(
                "id"
            )

            pics = []
            for pit_image in pit_images:
                pics.append(
                    {
                        "id": pit_image.id,
                        "img_url": general.cloudinary.build_image_url(
                            pit_image.img_id, pit_image.img_ver
                        ),
                        "img_title": pit_image.img_title,
                        "default": pit_image.default,
                        "pit_image_typ": pit_image.pit_image_typ,
                    }
                )

            team_response = {
                "team_no": team.team_no,
                "team_nm": team.team_nm,
                "pics": pics,
                "id": pit_response.id if pit_response is not None else None,
            }

            tmp_responses = []

            try:
                eti = team.eventteaminfo_set.get(
                    Q(event=current_event) & Q(team=team) & Q(void_ind="n")
                )
                tmp_responses.append({"question": "Rank", "answer": eti.rank})
            except EventTeamInfo.DoesNotExist:
                pass

            for question in questions:
                try:
                    answer = Answer.objects.get(
                        Q(response=pit_response.response)
                        & Q(void_ind="n")
                        & Q(question_id=question["id"])
                    ).value
                except Answer.DoesNotExist:
                    answer = "!FOUND"

                tmp_responses.append(
                    {
                        "question": (
                            " C: "
                            if question["question_conditional_on"] is not None
                            else ""
                        )
                        + question["question"],
                        "answer": answer,
                    }
                )

            team_response["responses"] = tmp_responses
            results.append(team_response)

    return {
        "teams": results,
        "current_season": current_season,
        "current_event": current_event,
    }


def save_robot_picture(file, team_no, pit_image_typ, img_title):
    current_event = scouting.util.get_current_event()

    sp = PitResponse.objects.get(
        Q(event=current_event)
        & Q(team_id=team_no)
        & Q(void_ind="n")
        & Q(response__void_ind="n")
    )

    response = general.cloudinary.upload_image(file)

    PitImage(
        pit_response=sp,
        pit_image_typ_id=pit_image_typ,
        img_id=response["public_id"],
        img_ver=str(response["version"]),
        img_title=img_title,
    ).save()

    return ret_message("Saved pit image successfully.")


def set_default_team_image(id):
    spi = PitImage.objects.get(Q(void_ind="n") & Q(id=id))

    for pi in spi.pit_response.pitimage_set.filter(
        Q(void_ind="n") & Q(pit_image_typ=spi.pit_image_typ)
    ):
        pi.default = False
        pi.save()

    spi.default = True
    spi.save()

    return spi


def get_team_data(team_no=None):
    current_event = scouting.util.get_current_event()

    sp = PitResponse.objects.get(
        Q(team_id=team_no)
        & Q(void_ind="n")
        & Q(response__void_ind="n")
        & Q(event=current_event)
    )

    response_answers = form.util.get_response_answers(sp.response)

    questions = []
    for response_answer in response_answers:
        response_answer["question"]["answer"] = response_answer["answer"]
        questions.append(response_answer["question"])

    pics = []

    for pic in sp.pitimage_set.filter(Q(void_ind="n")):
        pics.append(
            {
                "id": pic.id,
                "img_url": general.cloudinary.build_image_url(pic.img_id, pic.img_ver),
                "img_title": pic.img_title,
                "pit_image_typ": pic.pit_image_typ,
                "default": pic.default,
            }
        )

    return {
        "response_id": sp.response_id,
        "questions": questions,
        "pics": pics,
    }
