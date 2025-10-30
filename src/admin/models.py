from django.db import models
from user.models import User


class ErrorLog(models.Model):
    error_log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.PROTECT)
    path = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=1000, blank=True, null=True)
    exception = models.CharField(max_length=4000, blank=True, null=True)
    traceback = models.CharField(max_length=4000, blank=True, null=True)
    error_message = models.CharField(max_length=4000, blank=True, null=True)
    time = models.DateTimeField()
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"""ID: {self.error_log_id}
        Time: {self.time}
        User: {self.user.get_full_name()}
        Location: {self.path}
        Message: {self.message}
        Exception: {self.exception}"""
