# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User, Group


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
    date_end = models.DateTimeField()
    current = models.CharField(max_length=1, default='n')
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.event_id) + ' ' + self.event_nm


class QuestionType(models.Model):
    question_typ = models.CharField(primary_key=True, max_length=50)
    question_typ_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.question_typ + ' ' + self.question_typ_nm


class ScoutQuestionType(models.Model):
    sq_typ = models.CharField(primary_key=True, max_length=10)
    sq_nm = models.CharField(max_length=255)

    def __str__(self):
        return self.sq_typ + ' ' + self.sq_nm


class ScoutQuestion(models.Model):
    sq_id = models.AutoField(primary_key=True)
    season = models.ForeignKey(Season, models.DO_NOTHING)
    sq_typ = models.ForeignKey(ScoutQuestionType, models.PROTECT)
    question_typ = models.ForeignKey(QuestionType, models.PROTECT)
    question = models.CharField(max_length=1000)
    order = models.IntegerField()
    active = models.CharField(max_length=1)
    void_ind = models.CharField(max_length=1)

    def __str__(self):
        return str(self.sq_id) + ' ' + self.question


class QuestionOptions(models.Model):
    q_opt_id = models.AutoField(primary_key=True)
    option = models.CharField(max_length=255)
    sq = models.ForeignKey(ScoutQuestion, models.PROTECT)
    active = models.CharField(max_length=1, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.q_opt_id) + ' ' + self.option


class ScoutField(models.Model):
    scout_field_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team_no = models.ForeignKey(Team, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.scout_field_id


class ScoutFieldAnswer(models.Model):
    sfa_id = models.AutoField(primary_key=True)
    scout_field = models.ForeignKey(ScoutField, models.PROTECT)
    sq = models.ForeignKey(ScoutQuestion, models.PROTECT)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.sfa_id) + ' ' + self.answer


class ScoutPit(models.Model):
    scout_pit_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.PROTECT)
    team_no = models.ForeignKey(Team, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    img_id = models.CharField(max_length=500, blank=True, null=True)
    img_ver = models.CharField(max_length=500, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.scout_pit_id


class ScoutPitAnswer(models.Model):
    spa_id = models.AutoField(primary_key=True)
    scout_pit = models.ForeignKey(ScoutPit, models.PROTECT)
    sq = models.ForeignKey(ScoutQuestion, models.PROTECT)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.spa_id) + ' ' + self.answer


class ScoutAuthGroups(models.Model):
    scout_group = models.AutoField(unique=True, primary_key=True)
    auth_group_id = models.ForeignKey(Group, models.PROTECT)

    def __str__(self):
        return str(self.scout_group) + ' auth group: ' + str(self.auth_group_id)


class ScoutSchedule(models.Model):
    scout_sch_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.PROTECT)
    sq_typ = models.ForeignKey(ScoutQuestionType, models.PROTECT)
    st_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notified = models.CharField(max_length=1, default='n')
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' time: ' + self.st_time + ' - ' + self.end_time
