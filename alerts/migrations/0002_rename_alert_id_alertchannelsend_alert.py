# Generated by Django 4.2 on 2023-05-01 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alertchannelsend',
            old_name='alert_id',
            new_name='alert',
        ),
    ]