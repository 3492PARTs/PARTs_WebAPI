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

    teams = Team.objects.filter(teamCondition & Q(event=current_event)).order_by(
        "team_no"
    )

    results = []
    for team in teams:
        try:
            pit_response = PitResponse.objects.get(
                Q(team=team)
                & Q(event=current_event)
                & Q(void_ind="n")
                & Q(response__void_ind="n")
            )
        except PitResponse.DoesNotExist as e:
            pit_response = None

        pit_images = PitImage.objects.filter(Q(void_ind="n") & Q(scout_pit=pit_response)).order_by(
            "scout_pit_img_id"
        )

        pics = []
        for pit_image in pit_images:
            pics.append(
                {
                    "scout_pit_img_id": pit_image.scout_pit_img_id,
                    "pic": general.cloudinary.build_image_url(pit_image.img_id, pit_image.img_ver),
                    "default": pit_image.default,
                }
            )

        team_response = {
            "team_no": team.team_no,
            "team_nm": team.team_nm,
            "pics": pics,
            "scout_pit_id": pit_response.scout_pit_id if pit_response is not None else None,
        }

        tmp_responses = []

        try:
            eti = EventTeamInfo.objects.get(
                Q(event=current_event) & Q(team=team) & Q(void_ind="n")
            )
            tmp_responses.append({"question": "Rank", "answer": eti.rank})
        except EventTeamInfo.DoesNotExist:
            pass

        questions = form.util.get_questions("pit")

        if pit_response is not None:
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
                    {"question": (" C: " if question["question_conditional_on"] is not None else "") + question["question"], "answer": answer}
                )

                """
                for c in question.get("conditions", []):
                    answer = Answer.objects.get(
                        Q(response=pit_response.response)
                        & Q(void_ind="n")
                        & Q(question_id=c["question_to"]["question_id"])
                    )
                    tmp_responses.append(
                        {
                            "question": "C: "
                            + c["condition"]
                            + " "
                            + c["question_to"]["question"],
                            "answer": answer.value,
                        }
                    )
                """
        team_response["responses"] = tmp_responses
        results.append(team_response)

    return {
        "teams": results,
        "current_season": current_season,
        "current_event": current_event,
    }


def save_robot_picture(file, team_no):
    current_event = scouting.util.get_current_event()

    sp = PitResponse.objects.get(
        Q(event=current_event)
        & Q(team_no_id=team_no)
        & Q(void_ind="n")
        & Q(response__void_ind="n")
    )

    response = general.cloudinary.upload_image(file)

    PitImage(
        scout_pit=sp,
        img_id=response["public_id"],
        img_ver=str(response["version"]),
    ).save()

    return ret_message("Saved pit image successfully.")


def set_default_team_image(id):
    spi = PitImage.objects.get(Q(void_ind="n") & Q(scout_pit_img_id=id))

    for pi in spi.scout_pit.scoutpitimage_set.filter(Q(void_ind="n")):
        pi.default = False
        pi.save()

    spi.default = True
    spi.save()

    return spi


def get_team_data(team_no=None):
    current_event = scouting.util.get_current_event()

    sp = PitResponse.objects.get(
        Q(team_no=team_no)
        & Q(void_ind="n")
        & Q(response__void_ind="n")
        & Q(event=current_event)
    )

    response_answers = form.util.get_response_answers(
        sp.response
    )

    questions = []
    for response_answer in response_answers:
        response_answer["question"]["answer"] = response_answer["answer"]
        questions.append(response_answer["question"])

    pics = []

    for pic in sp.pitimage_set.filter(Q(void_ind="n")):
        pics.append(
            {
                "scout_pit_img_id": pic.scout_pit_img_id,
                "pic": general.cloudinary.build_image_url(pic.img_id, pic.img_ver),
                "default": pic.default,
            }
        )

    return {
        "response_id": sp.response_id,
        "questions": questions,
        "pics": pics,
    }
