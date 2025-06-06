# Generated by Django 5.1.5 on 2025-02-10 14:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0064_alter_dashboardactiveteam_team'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dashboard',
            name='active_team',
        ),
        migrations.AddField(
            model_name='dashboard',
            name='reference_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reference_team', to='scouting.team'),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='scouting.team'),
        ),
        migrations.DeleteModel(
            name='DashboardActiveTeam',
        ),
    ]
