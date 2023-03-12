# Generated by Django 4.0.3 on 2023-03-11 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scoutfieldschedule',
            name='notified',
        ),
        migrations.AddField(
            model_name='scoutfieldschedule',
            name='notification1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scoutfieldschedule',
            name='notification2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scoutfieldschedule',
            name='notification3',
            field=models.BooleanField(default=False),
        ),
    ]
