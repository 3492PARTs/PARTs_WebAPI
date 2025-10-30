# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import django
from django.db import models

from user.models import User


class CommunicationChannelType(models.Model):
    comm_typ = models.CharField(primary_key=True, max_length=50)
    comm_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.comm_typ} : {self.comm_nm}"


class AlertType(models.Model):
    alert_typ = models.CharField(primary_key=True, max_length=50)
    alert_typ_nm = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, null=True)
    body = models.CharField(max_length=4000, null=True)
    last_run = models.DateTimeField()
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.comp_lvl_typ} : {self.comp_lvl_typ_nm}"


class Alert(models.Model):
    id = models.AutoField(primary_key=True)
    alert_typ = models.ForeignKey(AlertType, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    subject = models.CharField(max_length=255)
    body = models.CharField(max_length=4000)
    url = models.CharField(max_length=4000, null=True)
    staged_time = models.DateTimeField(default=django.utils.timezone.now)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.subject}"


class ChannelSend(models.Model):
    id = models.AutoField(primary_key=True)
    comm_typ = models.ForeignKey(CommunicationChannelType, on_delete=models.PROTECT)
    alert = models.ForeignKey(Alert, on_delete=models.PROTECT)
    sent_time = models.DateTimeField(null=True)
    dismissed_time = models.DateTimeField(null=True)
    tries = models.IntegerField(default=0)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return str(self.id)


class AlertedResource(models.Model):
    id = models.AutoField(primary_key=True)
    alert_typ = models.ForeignKey(AlertType, on_delete=models.PROTECT, null=True)
    foreign_id = models.CharField(max_length=2000)
    time = models.DateTimeField(default=django.utils.timezone.now)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.subject}"
