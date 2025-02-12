# Generated by Django 5.1.5 on 2025-02-12 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0065_remove_dashboard_active_team_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dashboard',
            name='team',
        ),
        migrations.AddField(
            model_name='dashboard',
            name='teams',
            field=models.ManyToManyField(to='scouting.team'),
        ),
    ]
