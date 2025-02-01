# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

import django
from django.db import models
from django.contrib.auth.models import Group

import form.models
from user.models import User


class Season(models.Model):
    id = models.AutoField(primary_key=True)
    season = models.CharField(max_length=45)
    current = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.season}"


class Team(models.Model):
    team_no = models.IntegerField(primary_key=True)
    team_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.team_no} : {self.team_nm}"


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    teams = models.ManyToManyField(Team)
    event_nm = models.CharField(max_length=255)
    date_st = models.DateTimeField()
    event_cd = models.CharField(unique=True, max_length=10)
    event_url = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state_prov = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    location_name = models.CharField(max_length=255, null=True)
    gmaps_url = models.CharField(max_length=255, null=True)
    webcast_url = models.CharField(max_length=255, null=True)
    date_end = models.DateTimeField()
    timezone = models.CharField(max_length=255, null=True)
    current = models.CharField(max_length=1, default="n")
    competition_page_active = models.CharField(max_length=1, default="n")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.event_nm} : {self.season}"


class EventTeamInfo(models.Model):
    event = models.ForeignKey(Event, models.PROTECT)
    team = models.ForeignKey(Team, models.PROTECT)
    matches_played = models.IntegerField(null=True)
    qual_average = models.IntegerField(null=True)
    losses = models.IntegerField(null=True)
    wins = models.IntegerField(null=True)
    ties = models.IntegerField(null=True)
    rank = models.IntegerField(null=True)
    dq = models.IntegerField(null=True)
    void_ind = models.CharField(max_length=1, default="n")

    class Meta:
        unique_together = (("event", "team"),)

    def __str__(self):
        return f"Event: {self.event} : Team: {self.team}"


class CompetitionLevel(models.Model):
    comp_lvl_typ = models.CharField(primary_key=True, max_length=50)
    comp_lvl_typ_nm = models.CharField(max_length=255)
    comp_lvl_order = models.IntegerField()
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.comp_lvl_typ} : {self.comp_lvl_typ_nm}"


class Match(models.Model):
    match_key = models.CharField(primary_key=True, max_length=50)
    match_number = models.IntegerField()
    event = models.ForeignKey(Event, models.PROTECT)
    red_one = models.ForeignKey(
        Team, models.PROTECT, related_name="red_one_team", null=True
    )
    red_two = models.ForeignKey(
        Team, models.PROTECT, related_name="red_two_team", null=True
    )
    red_three = models.ForeignKey(
        Team, models.PROTECT, related_name="red_three_team", null=True
    )
    blue_one = models.ForeignKey(
        Team, models.PROTECT, related_name="blue_one_team", null=True
    )
    blue_two = models.ForeignKey(
        Team, models.PROTECT, related_name="blue_two_team", null=True
    )
    blue_three = models.ForeignKey(
        Team, models.PROTECT, related_name="blue_three_team", null=True
    )
    red_score = models.IntegerField(null=True)
    blue_score = models.IntegerField(null=True)
    comp_level = models.ForeignKey(CompetitionLevel, models.PROTECT)
    time = models.DateTimeField(null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.match_key} : {self.match_number} : {self.comp_level} : {self.event}"


class FieldForm(models.Model):
    id = models.AutoField(primary_key=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    img_id = models.CharField(max_length=500, blank=True, null=True)
    img_ver = models.CharField(max_length=500, blank=True, null=True)
    inv_img_id = models.CharField(max_length=500, blank=True, null=True)
    inv_img_ver = models.CharField(max_length=500, blank=True, null=True)
    full_img_id = models.CharField(max_length=500, blank=True, null=True)
    full_img_ver = models.CharField(max_length=500, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.season}"


class FieldResponse(models.Model):
    id = models.AutoField(primary_key=True)
    response = models.ForeignKey(form.models.Response, models.PROTECT, null=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team = models.ForeignKey(Team, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    time = models.DateTimeField(default=django.utils.timezone.now)
    match = models.ForeignKey(Match, models.PROTECT, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.team} : {self.match} : {self.event} : {self.user}"


class PitResponse(models.Model):
    id = models.AutoField(primary_key=True)
    response = models.ForeignKey(form.models.Response, models.PROTECT)
    event = models.ForeignKey(Event, models.PROTECT)
    team = models.ForeignKey(Team, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.team} : {self.event} : {self.user}"


class PitImageType(models.Model):
    pit_image_typ = models.CharField(primary_key=True, max_length=10)
    pit_image_nm = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.pit_image_typ} : {self.pit_image_nm}"


class PitImage(models.Model):
    id = models.AutoField(primary_key=True)
    pit_response = models.ForeignKey(PitResponse, models.PROTECT)
    pit_image_typ = models.ForeignKey(PitImageType, models.PROTECT)
    img_id = models.CharField(max_length=500, blank=True, null=True)
    img_ver = models.CharField(max_length=500, blank=True, null=True)
    img_title = models.CharField(max_length=2000, blank=True, null=True)
    default = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.pit_response}"


class ScoutAuthGroup(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.ForeignKey(Group, models.PROTECT)

    def __str__(self):
        return f"{self.id} : {self.group}"


class FieldSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.PROTECT)
    red_one = models.ForeignKey(
        User, models.PROTECT, related_name="red_one_user", null=True
    )
    red_two = models.ForeignKey(
        User, models.PROTECT, related_name="red_two_user", null=True
    )
    red_three = models.ForeignKey(
        User, models.PROTECT, related_name="red_three_user", null=True
    )
    blue_one = models.ForeignKey(
        User, models.PROTECT, related_name="blue_one_user", null=True
    )
    blue_two = models.ForeignKey(
        User, models.PROTECT, related_name="blue_two_user", null=True
    )
    blue_three = models.ForeignKey(
        User, models.PROTECT, related_name="blue_three_user", null=True
    )
    red_one_check_in = models.DateTimeField(null=True)
    red_two_check_in = models.DateTimeField(null=True)
    red_three_check_in = models.DateTimeField(null=True)
    blue_one_check_in = models.DateTimeField(null=True)
    blue_two_check_in = models.DateTimeField(null=True)
    blue_three_check_in = models.DateTimeField(null=True)
    st_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notification1 = models.BooleanField(default=False)
    notification2 = models.BooleanField(default=False)
    notification3 = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} time: {self.st_time} - {self.end_time}: {self.event}"


class ScheduleType(models.Model):
    sch_typ = models.CharField(primary_key=True, max_length=10)
    sch_nm = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.sch_typ} : {self.sch_nm}"


class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    sch_typ = models.ForeignKey(ScheduleType, models.PROTECT)
    event = models.ForeignKey(Event, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    st_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notified = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.user} : {self.sch_typ} : {self.st_time} - {self.end_time} : {self.event}"


class TeamNote(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team = models.ForeignKey(Team, models.PROTECT)
    match = models.ForeignKey(Match, models.PROTECT, null=True)
    user = models.ForeignKey(User, models.PROTECT)
    note = models.TextField()
    time = models.DateTimeField(default=django.utils.timezone.now)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.user} : {self.team} : {self.event} : {self.match}"


class QuestionType(models.Model):
    id = models.AutoField(primary_key=True)
    question_typ = models.ForeignKey(
        form.models.QuestionType, models.PROTECT, related_name="scout_question_type"
    )
    scorable = models.CharField(max_length=1, default="n")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.question_typ}"


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        form.models.Question, models.PROTECT, related_name="scout_question"
    )
    season = models.ForeignKey(Season, models.PROTECT, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.question}"


class QuestionFlow(models.Model):
    id = models.AutoField(primary_key=True)
    flow = models.ForeignKey(
        form.models.Flow, models.PROTECT, related_name="scout_question_flow"
    )
    season = models.ForeignKey(Season, models.PROTECT, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} {self.flow}"


class UserInfo(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.PROTECT, related_name="scouting_user_info")
    under_review = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.user}"


class MatchStrategy(models.Model):
    id = models.AutoField(primary_key=True)
    match = models.ForeignKey(Match, models.PROTECT, null=True)
    user = models.ForeignKey(User, models.PROTECT)
    strategy = models.TextField()
    img_id = models.CharField(max_length=500, blank=True, null=True)
    img_ver = models.CharField(max_length=500, blank=True, null=True)
    time = models.DateTimeField(default=django.utils.timezone.now)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.match} : {self.user}"


class AllianceSelection(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team = models.ForeignKey(Team, models.PROTECT)
    note = models.TextField()
    order = models.IntegerField()
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.order} : {self.team}"
