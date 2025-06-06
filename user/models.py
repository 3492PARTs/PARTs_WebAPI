import django
from django.db import models
from django.contrib.auth.models import (
    Permission,
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class Link(models.Model):
    id = models.AutoField(primary_key=True)
    permission = models.ForeignKey(Permission, models.PROTECT, null=True)
    menu_name = models.CharField(max_length=255)
    routerlink = models.CharField(max_length=255)
    order = models.IntegerField()

    def __str__(self):
        return str(self.id) + " " + self.menu_name


class PhoneType(models.Model):
    id = models.AutoField(primary_key=True)
    carrier = models.CharField(max_length=255)
    phone_type = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} : {self.carrier} :{self.phone_type}"


class ProfileManager(BaseUserManager):
    def create_user(self, email, username, password=None, first_name="", last_name=""):
        if not email:
            raise ValueError("Email required")
        if not username:
            raise ValueError("Username required")
        user = self.model(
            username=username.lower(),
            email=self.normalize_email(email.lower()),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password, first_name, last_name):
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # user model required fields
    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=None, null=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # extra info
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    phone = models.CharField(max_length=10, blank=True, null=True)
    phone_type = models.ForeignKey(PhoneType, models.PROTECT, blank=True, null=True)
    discord_user_id = models.CharField(max_length=1000, blank=True, null=True)
    img_id = models.CharField(max_length=500, blank=True, null=True)
    img_ver = models.CharField(max_length=500, blank=True, null=True)

    # sets what the user will log in with
    USERNAME_FIELD = "username"

    # what is required by the model (do not put username and password here, this is used for the create superuser function which has those by default)
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    # user manager class
    objects = ProfileManager()

    def __str__(self):
        return f"User name: {self.username} email: {self.email} "

    def has_perm(self, perm, obj=None):
        # TODO revisit this
        return self.is_superuser

    def has_module_perms(self, app_Label):
        # TODO revisit this
        return True

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
