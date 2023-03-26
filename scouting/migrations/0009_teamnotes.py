# Generated by Django 4.0.3 on 2023-03-26 13:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scouting', '0008_alter_schedule_notified'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamNotes',
            fields=[
                ('team_note_id', models.AutoField(primary_key=True, serialize=False)),
                ('note', models.TextField()),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.event')),
                ('match', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='scouting.match')),
                ('team_no', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
