# Generated by Django 4.0.3 on 2023-03-19 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0005_schedule_and_event_team_info_event_field_Rename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventteaminfo',
            name='dq',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='eventteaminfo',
            name='losses',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='eventteaminfo',
            name='matches_played',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='eventteaminfo',
            name='qual_average',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='eventteaminfo',
            name='rank',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='eventteaminfo',
            name='ties',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='eventteaminfo',
            name='wins',
            field=models.IntegerField(null=True),
        ),
    ]