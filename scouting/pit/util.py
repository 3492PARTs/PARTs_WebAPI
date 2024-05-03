from django.db.models import Q
import cloudinary

from form.models import QuestionAnswer
from general.security import ret_message
import scouting
import form
from scouting.models import EventTeamInfo, ScoutPit, ScoutPitImage, Team


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
    for t in teams:
        try:
            sp = ScoutPit.objects.get(
                Q(team_no=t)
                & Q(event=current_event)
                & Q(void_ind="n")
                & Q(response__void_ind="n")
            )
        except ScoutPit.DoesNotExist as e:
            sp = None

        spis = ScoutPitImage.objects.filter(Q(void_ind="n") & Q(scout_pit=sp)).order_by(
            "scout_pit_img_id"
        )

        pics = []
        for spi in spis:
            pics.append(
                {
                    "scout_pit_img_id": spi.scout_pit_img_id,
                    "pic": cloudinary.CloudinaryImage(
                        spi.img_id, version=spi.img_ver
                    ).build_url(secure=True),
                    "default": spi.default,
                }
            )

        team_response = {
            "team_no": t.team_no,
            "team_nm": t.team_nm,
            "pics": pics,
            "scout_pit_id": sp.scout_pit_id if sp is not None else None,
        }

        tmp_responses = []

        try:
            eti = EventTeamInfo.objects.get(
                Q(event=current_event) & Q(team_no=t.team_no) & Q(void_ind="n")
            )
            tmp_responses.append({"question": "Rank", "answer": eti.rank})
        except EventTeamInfo.DoesNotExist:
            x = 1

        questions = form.util.get_questions_with_conditions("pit")

        if sp is not None:
            for q in questions:
                answer = QuestionAnswer.objects.get(
                    Q(response=sp.response)
                    & Q(void_ind="n")
                    & Q(question_id=q["question_id"])
                )
                tmp_responses.append(
                    {"question": q["question"], "answer": answer.answer}
                )

                for c in q.get("conditions", []):
                    answer = QuestionAnswer.objects.get(
                        Q(response=sp.response)
                        & Q(void_ind="n")
                        & Q(question_id=c["question_to"]["question_id"])
                    )
                    tmp_responses.append(
                        {
                            "question": "C: "
                            + c["condition"]
                            + " "
                            + c["question_to"]["question"],
                            "answer": answer.answer,
                        }
                    )

        team_response["responses"] = tmp_responses
        results.append(team_response)

    return {
        "teams": results,
        "current_season": current_season,
        "current_event": current_event,
    }


def save_robot_picture(file, team_no):
    current_event = scouting.util.get_current_event()

    if not allowed_file(file.content_type):
        raise Exception("Invalid file type.")

    sp = ScoutPit.objects.get(
        Q(event=current_event)
        & Q(team_no_id=team_no)
        & Q(void_ind="n")
        & Q(response__void_ind="n")
    )

    response = cloudinary.uploader.upload(file)

    ScoutPitImage(
        scout_pit=sp,
        img_id=response["public_id"],
        img_ver=str(response["version"]),
    ).save()

    return ret_message("Saved pit image successfully.")


def allowed_file(filename):
    """Returns whether a filename's extension indicates that it is an image.
    :param str filename: A filename.
    :return: Whether the filename has an recognized image file extension
    :rtype: bool"""
    return filename.rsplit("/", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}


def set_default_team_image(id):
    spi = ScoutPitImage.objects.get(Q(void_ind="n") & Q(scout_pit_img_id=id))

    for pi in spi.scout_pit.scoutpitimage_set.filter(Q(void_ind="n")):
        pi.default = False
        pi.save()

    spi.default = True
    spi.save()

    return spi


def get_team_data(team_no=None):
    current_event = scouting.util.get_current_event()

    sp = ScoutPit.objects.get(
        Q(team_no=team_no)
        & Q(void_ind="n")
        & Q(response__void_ind="n")
        & Q(event=current_event)
    )

    scout_questions = form.util.get_question_with_conditions_response_answers(
        sp.response
    )

    pics = []

    for pic in sp.scoutpitimage_set.filter(Q(void_ind="n")):
        pics.append(
            {
                "scout_pit_img_id": pic.scout_pit_img_id,
                "pic": cloudinary.CloudinaryImage(
                    pic.img_id, version=pic.img_ver
                ).build_url(secure=True),
                "default": pic.default,
            }
        )

    return {
        "response_id": sp.response_id,
        "questions": scout_questions,
        "pics": pics,
    }
