from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from user.models import User


class ResourceType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2000, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id} : {self.name}"


class Resource(models.Model):
    id = models.AutoField(primary_key=True)
    resource_type = models.ForeignKey(ResourceType, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2000, blank=True, null=True)
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id} : {self.name}"

    def is_checked_out(self) -> bool:
        """Check if this resource currently has an open checkout (not checked back in)."""
        return self.resourcecheckout_set.filter(
            time_in__isnull=True, void_ind="n"
        ).exists()

    @property
    def checked_out(self) -> bool:
        return self.is_checked_out()


class ResourceCheckOut(models.Model):
    id = models.AutoField(primary_key=True)
    resource = models.ForeignKey(Resource, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    time_out = models.DateTimeField(default=now)
    time_in = models.DateTimeField(null=True, blank=True)
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id} : {self.resource} : {self.user}"

    def is_checked_in(self) -> bool:
        return self.time_in is not None
