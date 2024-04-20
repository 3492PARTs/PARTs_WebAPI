from django.db import transaction
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import scouting
from form.models import QuestionAnswer, Question
from scouting.models import Season, Team, Event, ScoutPit, EventTeamInfo, ScoutPitImage
import scouting.pit
import scouting.pit.util
from .serializers import (
    InitSerializer,
    PitTeamDataSerializer,
    ScoutAnswerSerializer,
    ScoutPitResponseSerializer,
    ScoutPitResponsesSerializer,
    TeamSerializer,
)
from rest_framework.views import APIView
from general.security import ret_message, has_access
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.db.models import Q, Prefetch
from rest_framework.response import Response
import form.util

auth_obj = "scoutpit"
auth_view_obj = "scoutPitResults"
app_url = "scouting/pit/"


class SavePicture(APIView):
    """
    API endpoint to save a robot picture
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "save-picture/"

    def save_file(self, file, team_no):

        try:
            current_season = Season.objects.get(current="y")
        except Exception as e:
            return ret_message(
                "No season set, see an admin.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
                e,
            )

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current="y"))
        except Exception as e:
            return ret_message(
                "No event set, see an admin.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
                e,
            )

        if not allowed_file(file.content_type):
            return ret_message(
                "Invalid file type.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
            )

        try:
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

        except Exception as e:
            return ret_message(
                "An error occurred while saving the image.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
                e,
            )

        return ret_message("Saved Image Successfully.")

    def post(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                file_obj = request.FILES["file"]
                ret = self.save_file(file_obj, request.data.get("team_no", ""))
                return ret
            except Exception as e:
                return ret_message(
                    "An error occurred while saving robot picture.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class Responses(APIView):
    """
    API endpoint to get scout pit results for the selected teams
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "responses/"

    def get(self, request, format=None):
        if (
            has_access(request.user.id, auth_obj)
            or has_access(request.user.id, auth_view_obj)
            or has_access(request.user.id, "scoutFieldResults")
        ):
            try:
                ret = scouting.pit.util.get_responses(
                    request, request.query_params.get("team", None)
                )

                if type(ret) == Response:
                    return ret

                serializer = ScoutPitResponsesSerializer(ret)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting pit results.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SetDefaultPitImage(APIView):
    """
    API endpoint to set a default image for a team's pit scouting result
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "set-default-pit-image/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                spi = ScoutPitImage.objects.get(
                    Q(void_ind="n")
                    & Q(
                        scout_pit_img_id=request.query_params.get(
                            "scout_pit_img_id", None
                        )
                    )
                )

                for pi in spi.scout_pit.scoutpitimage_set.filter(Q(void_ind="n")):
                    pi.default = False
                    pi.save()

                spi.default = True
                spi.save()

                return ret_message("Successfully set the team" "s default image.")
            except Exception as e:
                return ret_message(
                    "An error occurred while getting team data.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class TeamData(APIView):
    """
    API endpoint to get scout pit team data
    for an individual team, used to get the data for the scouting screen not results screen
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "team-data/"

    def get_questions(self, team_num):

        try:
            current_season = Season.objects.get(current="y")
        except Exception as e:
            return ret_message(
                "No season set, see an admin.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
                e,
            )

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current="y"))
        except Exception as e:
            return ret_message(
                "No event set, see an admin",
                True,
                app_url + self.endpoint,
                self.request.user.id,
                e,
            )

        sp = ScoutPit.objects.get(
            Q(team_no=team_num) & Q(void_ind="n") & Q(event=current_event)
        )

        scout_questions = []

        sqs = form.util.get_questions_with_conditions("pit")

        pics = []
        for sq in sqs:
            try:
                spa = QuestionAnswer.objects.get(
                    Q(response_id=sp.response_id) & Q(question_id=sq["question_id"])
                )
            except Exception as e:
                spa = QuestionAnswer(answer="")

            sq["answer"] = spa.answer

            for c in sq.get("conditions", []):
                try:
                    spa = QuestionAnswer.objects.get(
                        Q(response_id=sp.response_id)
                        & Q(question_id=c["question_to"]["question_id"])
                    )
                except Exception as e:
                    spa = QuestionAnswer(answer="")

                c["question_to"]["answer"] = spa.answer
            scout_questions.append(sq)

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

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions(request.query_params.get("team_num", None))
                serializer = PitTeamDataSerializer(
                    req,
                )
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting team data.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


def allowed_file(filename):
    """Returns whether a filename's extension indicates that it is an image.
    :param str filename: A filename.
    :return: Whether the filename has an recognized image file extension
    :rtype: bool"""
    return filename.rsplit("/", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}
