# Generated by Django 2.2.7 on 2019-11-06 02:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_id', models.AutoField(primary_key=True, serialize=False)),
                ('event_nm', models.CharField(max_length=255)),
                ('date_st', models.DateTimeField()),
                ('event_cd', models.CharField(max_length=10, unique=True)),
                ('date_end', models.DateTimeField()),
                ('void_ind', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'db_table': 'event',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('question_typ', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('question_typ_nm', models.CharField(max_length=255)),
                ('void_ind', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'question_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScoutField',
            fields=[
                ('scout_field_id', models.AutoField(primary_key=True, serialize=False)),
                ('void_ind', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'scout_field',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScoutFieldAnswer',
            fields=[
                ('sfa_id', models.AutoField(primary_key=True, serialize=False)),
                ('answer', models.CharField(blank=True, max_length=1000, null=True)),
                ('void_ind', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'scout_field_answer',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScoutFieldQuestion',
            fields=[
                ('sfq_id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=1000)),
                ('void_ind', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'scout_field_question',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScoutPit',
            fields=[
                ('scout_pit_id', models.AutoField(primary_key=True, serialize=False)),
                ('img_id', models.CharField(blank=True, max_length=500, null=True)),
                ('img_ver', models.CharField(blank=True, max_length=500, null=True)),
                ('void_ind', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'scout_pit',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScoutPitAnswer',
            fields=[
                ('spa_id', models.AutoField(primary_key=True, serialize=False)),
                ('answer', models.CharField(blank=True, max_length=1000, null=True)),
                ('void_ind', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'scout_pit_answer',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScoutPitQuestion',
            fields=[
                ('spq_id', models.IntegerField(primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=1000)),
                ('void_ind', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'scout_pit_question',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('season_id', models.IntegerField(primary_key=True, serialize=False)),
                ('season', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'season',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('team_no', models.IntegerField(primary_key=True, serialize=False)),
                ('team_nm', models.CharField(max_length=255)),
                ('void_ind', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'db_table': 'team',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EventTeamXref',
            fields=[
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='api.Event')),
            ],
            options={
                'db_table': 'event_team_xref',
                'managed': False,
            },
        ),
    ]
