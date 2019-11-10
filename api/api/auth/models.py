from django.db import models


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)
    # user = models.ForeignKey(AuthUser, models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class Contact(models.Model):
    contact_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    phone_no = models.CharField(max_length=20)
    address_1 = models.CharField(max_length=100)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    providence = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    audit_user_crea = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name="contact_user_crea_id")
    audit_user_crea_dtm = models.DateTimeField()
    audit_user_upd = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name="contact_user_upd_id")
    audit_user_upd_dtm = models.DateTimeField(blank=True, null=True)
    void_ind = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contact'
