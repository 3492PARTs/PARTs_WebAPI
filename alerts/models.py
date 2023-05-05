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


class AlertCommunicationChannelType(models.Model):
    alert_comm_typ = models.CharField(primary_key=True, max_length=50)
    alert_comm_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.alert_comm_typ)


class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    alert_subject = models.CharField(max_length=255)
    alert_body = models.CharField(max_length=4000)
    staged_time = models.DateTimeField(default=django.utils.timezone.now)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.alert_id)


class AlertChannelSend(models.Model):
    alert_channel_send_id = models.AutoField(primary_key=True)
    alert_comm_typ = models.ForeignKey(AlertCommunicationChannelType, on_delete=models.PROTECT)
    alert = models.ForeignKey(Alert, on_delete=models.PROTECT)
    sent_time = models.DateTimeField(null=True)
    dismissed_time = models.DateTimeField(null=True)
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.alert_channel_send_id)
