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
    season_id = models.AutoField(primary_key=True)
    season = models.CharField(max_length=45)
    current = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.season_id) + ' ' + self.season


class Team(models.Model):
    team_no = models.IntegerField(primary_key=True)
    team_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.team_no) + ' ' + self.team_nm


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    team_no = models.ManyToManyField(Team)
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
    current = models.CharField(max_length=1, default='n')
    competition_page_active = models.CharField(max_length=1, default='n')
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.event_id) + ' ' + self.event_nm


class EventTeamInfo(models.Model):
    event = models.ForeignKey(Event, models.PROTECT)
    team_no = models.ForeignKey(Team, models.PROTECT)
    matches_played = models.IntegerField(null=True)
    qual_average = models.IntegerField(null=True)
    losses = models.IntegerField(null=True)
    wins = models.IntegerField(null=True)
    ties = models.IntegerField(null=True)
    rank = models.IntegerField(null=True)
    dq = models.IntegerField(null=True)
    void_ind = models.CharField(max_length=1, default='n')

    class Meta:
        unique_together = (('event', 'team_no'),)

    def __str__(self):
        return "Event {event}. Team {team}. ".format(event=self.event.event_id, team=self.team_no.team_no)


class CompetitionLevel(models.Model):
    comp_lvl_typ = models.CharField(primary_key=True, max_length=50)
    comp_lvl_typ_nm = models.CharField(max_length=255)
    comp_lvl_order = models.IntegerField()
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.comp_lvl_typ + ' ' + self.comp_lvl_typ_nm


class Match(models.Model):
    match_id = models.CharField(primary_key=True, max_length=50)
    match_number = models.IntegerField()
    event = models.ForeignKey(Event, models.PROTECT)
    red_one = models.ForeignKey(
        Team, models.PROTECT, related_name='red_one_team', null=True)
    red_two = models.ForeignKey(
        Team, models.PROTECT, related_name='red_two_team', null=True)
    red_three = models.ForeignKey(
        Team, models.PROTECT, related_name='red_three_team', null=True)
    blue_one = models.ForeignKey(
        Team, models.PROTECT, related_name='blue_one_team', null=True)
    blue_two = models.ForeignKey(
        Team, models.PROTECT, related_name='blue_two_team', null=True)
    blue_three = models.ForeignKey(
        Team, models.PROTECT, related_name='blue_three_team', null=True)
    red_score = models.IntegerField(null=True)
    blue_score = models.IntegerField(null=True)
    comp_level = models.ForeignKey(CompetitionLevel, models.PROTECT)
    time = models.DateTimeField(null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return 'match: ' + self.event.event_nm + ' ' + self.comp_level + ' match no: ' + self.match_number


class ScoutField(models.Model):
    scout_field_id = models.AutoField(primary_key=True)
    response_id_tmp = models.IntegerField(null=True)
    response = models.ForeignKey(form.models.Response, models.PROTECT, null=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team_no = models.ForeignKey(Team, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    time = models.DateTimeField(default=django.utils.timezone.now)
    match = models.ForeignKey(Match, models.PROTECT, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.scout_field_id


class ScoutPit(models.Model):
    scout_pit_id = models.AutoField(primary_key=True)
    response_id_tmp = models.IntegerField(null=True)
    response = models.ForeignKey(form.models.Response, models.PROTECT, null=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team_no = models.ForeignKey(Team, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    img_id = models.CharField(max_length=500, blank=True, null=True)
    img_ver = models.CharField(max_length=500, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.scout_pit_id


class ScoutAuthGroups(models.Model):
    scout_group = models.AutoField(unique=True, primary_key=True)
    auth_group_id = models.ForeignKey(Group, models.PROTECT)

    def __str__(self):
        return str(self.scout_group) + ' auth group: ' + str(self.auth_group_id)


class ScoutFieldSchedule(models.Model):
    scout_field_sch_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.PROTECT)
    red_one = models.ForeignKey(
        User, models.PROTECT, related_name='red_one_user', null=True)
    red_two = models.ForeignKey(
        User, models.PROTECT, related_name='red_two_user', null=True)
    red_three = models.ForeignKey(
        User, models.PROTECT, related_name='red_three_user', null=True)
    blue_one = models.ForeignKey(
        User, models.PROTECT, related_name='blue_one_user', null=True)
    blue_two = models.ForeignKey(
        User, models.PROTECT, related_name='blue_two_user', null=True)
    blue_three = models.ForeignKey(
        User, models.PROTECT, related_name='blue_three_user', null=True)
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
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.scout_field_sch_id + ' time: ' + self.st_time + ' - ' + self.end_time


class ScheduleType(models.Model):
    sch_typ = models.CharField(primary_key=True, max_length=10)
    sch_nm = models.CharField(max_length=255)

    def __str__(self):
        return self.sch_typ + ' ' + self.sch_nm


class Schedule(models.Model):
    sch_id = models.AutoField(primary_key=True)
    sch_typ = models.ForeignKey(ScheduleType, models.PROTECT)
    event = models.ForeignKey(Event, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    st_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notified = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' time: ' + self.st_time + ' - ' + self.end_time


class TeamNotes(models.Model):
    team_note_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team_no = models.ForeignKey(Team, models.PROTECT)
    match = models.ForeignKey(Match, models.PROTECT, null=True)
    user = models.ForeignKey(User, models.PROTECT)
    note = models.TextField()
    time = models.DateTimeField(default=django.utils.timezone.now)
    void_ind = models.CharField(max_length=1, default='n')


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question_id_tmp = models.IntegerField(null=True)
    question = models.ForeignKey(form.models.Question, models.PROTECT, related_name='form_question')
    season = models.ForeignKey(Season, models.PROTECT, null=True)
    scorable = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default='n')

