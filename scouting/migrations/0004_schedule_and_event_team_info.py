# Generated by Django 4.0.3 on 2023-03-19 19:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scouting', '0003_multiple_notifications'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventTeamInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matches_played', models.IntegerField()),
                ('qual_average', models.IntegerField()),
                ('losses', models.IntegerField()),
                ('wins', models.IntegerField()),
                ('ties', models.IntegerField()),
                ('rank', models.IntegerField()),
                ('dq', models.IntegerField()),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.event')),
                ('team_no', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.team')),
            ],
            options={
                'unique_together': {('event_id', 'team_no')},
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('sch_id', models.AutoField(primary_key=True, serialize=False)),
                ('st_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('notified', models.CharField(default='n', max_length=1)),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.event')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleType',
            fields=[
                ('sch_typ', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('sch_nm', models.CharField(max_length=255)),
            ],
        ),
        migrations.DeleteModel(
            name='ScoutPitSchedule',
        ),
        migrations.AddField(
            model_name='schedule',
            name='sch_typ',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.scheduletype'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
