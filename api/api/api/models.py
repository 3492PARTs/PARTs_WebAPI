# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    season = models.ForeignKey('Season', models.DO_NOTHING, blank=True, null=True)
    event_nm = models.CharField(max_length=255)
    date_st = models.DateTimeField()
    event_cd = models.CharField(unique=True, max_length=10)
    date_end = models.DateTimeField()
    current = models.CharField(max_length=1)
    void_ind = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event'


class EventTeamXref(models.Model):
    event = models.ForeignKey(Event, models.DO_NOTHING, primary_key=True)
    team_no = models.ForeignKey('Team', models.DO_NOTHING, db_column='team_no')

    class Meta:
        managed = False
        db_table = 'event_team_xref'
        unique_together = (('event', 'team_no'),)


class QuestionOptionType(models.Model):
    q_opt_typ_cd = models.CharField(primary_key=True, max_length=255)
    q_opt_nm = models.CharField(max_length=255, blank=True, null=True)
    void_ind = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'question_option_type'


class QuestionOptions(models.Model):
    q_opt_id = models.AutoField(primary_key=True)
    q_opt_typ_cd = models.ForeignKey(QuestionOptionType, models.DO_NOTHING, db_column='q_opt_typ_cd', blank=True, null=True)
    option = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'question_options'


class QuestionType(models.Model):
    question_typ = models.CharField(primary_key=True, max_length=50)
    question_typ_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'question_type'


class ScoutField(models.Model):
    scout_field_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    team_no = models.ForeignKey('Team', models.DO_NOTHING, db_column='team_no')
    void_ind = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'scout_field'


class ScoutFieldAnswer(models.Model):
    sfa_id = models.AutoField(primary_key=True)
    scout_field = models.ForeignKey(ScoutField, models.DO_NOTHING)
    sfq = models.ForeignKey('ScoutFieldQuestion', models.DO_NOTHING)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    void_ind = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'scout_field_answer'


class ScoutFieldQuestion(models.Model):
    sfq_id = models.AutoField(primary_key=True)
    season = models.ForeignKey('Season', models.DO_NOTHING)
    question_typ = models.ForeignKey(QuestionType, models.DO_NOTHING, db_column='question_typ')
    q_opt_typ_cd = models.ForeignKey(QuestionOptionType, models.DO_NOTHING, db_column='q_opt_typ_cd', blank=True, null=True)
    question = models.CharField(max_length=1000)
    order = models.IntegerField()
    void_ind = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'scout_field_question'


class ScoutPit(models.Model):
    scout_pit_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    team_no = models.ForeignKey('Team', models.DO_NOTHING, db_column='team_no')
    img_id = models.CharField(max_length=500, blank=True, null=True)
    img_ver = models.CharField(max_length=500, blank=True, null=True)
    void_ind = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'scout_pit'


class ScoutPitAnswer(models.Model):
    spa_id = models.AutoField(primary_key=True)
    scout_pit = models.ForeignKey(ScoutPit, models.DO_NOTHING)
    spq = models.ForeignKey('ScoutPitQuestion', models.DO_NOTHING)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    void_ind = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'scout_pit_answer'


class ScoutPitQuestion(models.Model):
    spq_id = models.IntegerField(primary_key=True)
    season = models.ForeignKey('Season', models.DO_NOTHING)
    question_typ = models.ForeignKey(QuestionType, models.DO_NOTHING, db_column='question_typ', blank=True, null=True)
    q_opt_typ_cd = models.ForeignKey(QuestionOptionType, models.DO_NOTHING, db_column='q_opt_typ_cd', blank=True, null=True)
    question = models.CharField(max_length=1000)
    void_ind = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'scout_pit_question'


class Season(models.Model):
    season_id = models.AutoField(primary_key=True)
    season = models.CharField(max_length=45)
    current = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'season'


class Team(models.Model):
    team_no = models.IntegerField(primary_key=True)
    team_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team'
