import django
from django.db import models

# Create your models here.
class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    message_type = models.CharField(max_length=4000, blank=True, null=True)
    message_data = models.CharField(max_length=4000, blank=True, null=True)
    time = models.DateTimeField(default=django.utils.timezone.now)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.message_id} message type: {self.message_type} data: {self.message_data}"
