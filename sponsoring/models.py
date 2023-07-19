# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import datetime

import django
from django.db import models
from django.contrib.auth.models import Group
from pytz import utc

from scouting.models import Season, ScoutField, ScoutPit
from user.models import User


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_nm = models.CharField(max_length=255)
    item_desc = models.TextField()
    quantity = models.IntegerField()
    void_ind = models.CharField(max_length=1, default='n')

    def __str__(self):
        return self.item_id + ' ' + self.item_nm


class Sponsor(models.Model):
    sponsor_id = models.AutoField(primary_key=True)
    sponsor_nm = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return self.sponsor_id + ' ' + self.sponsor_nm


class ItemSponsor(models.Model):
    item_sponsor_id = models.AutoField(primary_key=True)
    item_id = models.ForeignKey(Item, models.PROTECT)
    sponsor_id = models.ForeignKey(Sponsor, models.PROTECT)
    quantity = models.IntegerField()

    def __str__(self):
        return self.item_sponsor_id + ' ' + self.quantity
