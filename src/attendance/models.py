# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from user.models import User
from scouting.models import Season


class Meeting(models.Model):
    id = models.AutoField(primary_key=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    title = models.CharField(max_length=2000)
    description = models.CharField(max_length=4000)
    start = models.DateTimeField(default=now)
    end = models.DateTimeField(null=True)
    bonus = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id} : {self.title} : {self.start}"


class AttendanceApprovalType(models.Model):
    approval_typ = models.CharField(primary_key=True, max_length=50)
    approval_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.approval_typ} : {self.approval_nm}"


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, null=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    time_in = models.DateTimeField(default=now)
    time_out = models.DateTimeField(null=True)
    absent = models.BooleanField(default=False)
    approval_typ = models.ForeignKey(AttendanceApprovalType, on_delete=models.PROTECT)
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.id} : {self.user} : {self.time_in}"

    def is_unapproved(self) -> bool:
        """Check if attendance is in unapproved state."""
        return self.approval_typ.approval_typ == "unapp"

    def is_approved(self) -> bool:
        """Check if attendance has been approved."""
        return self.approval_typ.approval_typ == "app"

    def is_rejected(self) -> bool:
        """Check if attendance has been rejected."""
        return self.approval_typ.approval_typ == "rej"
