# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import datetime

import django
from django.db import models
from django.contrib.auth.models import Group
from pytz import utc

from scouting.models import Season, ScoutField
from user.models import User


class QuestionType(models.Model):
    question_typ = models.CharField(primary_key=True, max_length=50)
    question_typ_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.question_typ + ' ' + self.question_typ_nm


class Type(models.Model):
    form_typ = models.CharField(primary_key=True, max_length=10)
    form_nm = models.CharField(max_length=255)

    def __str__(self):
        return self.form_typ + ' ' + self.form_nm


class SubType(models.Model):
    form_sub_typ = models.CharField(primary_key=True, max_length=10)
    form_sub_nm = models.CharField(max_length=255)
    form_typ = models.ForeignKey(Type, models.PROTECT)

    def __str__(self):
        return self.form_sub_typ + ' ' + self.form_sub_nm


class Question(models.Model):
    q_id = models.AutoField(primary_key=True)
    season = models.ForeignKey(Season, models.PROTECT, null=True)
    form_typ = models.ForeignKey(Type, models.PROTECT)
    form_sub_typ = models.ForeignKey(SubType, models.PROTECT, null=True)
    question_typ = models.ForeignKey(QuestionType, models.PROTECT)
    question = models.CharField(max_length=1000)
    order = models.IntegerField()
    active = models.CharField(max_length=1)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.sq_id) + ' ' + self.question


class QuestionOption(models.Model):
    q_opt_id = models.AutoField(primary_key=True)
    option = models.CharField(max_length=255)
    q_id = models.ForeignKey(Question, models.PROTECT)
    active = models.CharField(max_length=1, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.q_opt_id) + ' ' + self.option


class FormResponse(models.Model):
    fr_id = models.AutoField(primary_key=True)
    time = models.DateTimeField(default=django.utils.timezone.now)


class QuestionAnswer(models.Model):
    qa_id = models.AutoField(primary_key=True)
    scout_field = models.ForeignKey(ScoutField, models.PROTECT, null=True, related_name='scout_field')
    scout_pit = models.ForeignKey(ScoutField, models.PROTECT, null=True, related_name='scout_pit')
    form_response = models.ForeignKey(FormResponse, models.PROTECT, null=True, related_name='form_response')
    q_id = models.ForeignKey(Question, models.PROTECT)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.sfa_id) + ' ' + self.answer

