# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import django
from django.db import models
from simple_history.models import HistoricalRecords

from user.models import User
from scouting.models import Season


class Meeting(models.Model):
    id = models.AutoField(primary_key=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    title = models.CharField(2000)
    description = models.CharField(4000)
    start = models.DateTimeField(default=django.utils.timezone.now)
    end = models.DateTimeField(null=True)
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id} : {self.user} : {self.time}"


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, null=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    time_in = models.DateTimeField(default=django.utils.timezone.now)
    time_out = models.DateTimeField(null=True)
    absent = models.BooleanField(default=False)
    bonus_approved = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id} : {self.user} : {self.time}"
