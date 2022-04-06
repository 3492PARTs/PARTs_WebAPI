from django.db import models
from user.models import User


class ErrorLog(models.Model):
    error_log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.PROTECT)
    path = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=1000, blank=True, null=True)
    exception = models.CharField(max_length=4000, blank=True, null=True)
    time = models.DateTimeField()
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return str(self.error_log_id) + ' user: ' + self.user.first_name + ' ' + self.user.last_name + \
            ' location: ' + self.path + ' msg: ' + \
            self.message + ' exc: ' + self.exception + ' time: ' + self.time
