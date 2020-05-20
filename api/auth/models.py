from django.db import models
from django.contrib.auth.models import Permission, User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserLinks(models.Model):
    user_links_id = models.AutoField(primary_key=True)
    permission = models.ForeignKey(Permission, models.PROTECT)
    menu_name = models.CharField(max_length=255)
    routerlink = models.CharField(max_length=255)
    order = models.IntegerField()

    def __str__(self):
        return str(self.user_links_id) + ' ' + self.menu_name


class PhoneType(models.Model):
    phone_type_id = models.AutoField(primary_key=True)
    carrier = models.CharField(max_length=255)
    phone_type = models.CharField(max_length=255)

    def __str__(self):
        return str(self.phone_type_id) + ' ' + self.carrier + ' ' + self.phone_type


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    phone_type = models.ForeignKey(PhoneType, models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' ' + self.phone + ' ' + str(self.phone_type)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


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
