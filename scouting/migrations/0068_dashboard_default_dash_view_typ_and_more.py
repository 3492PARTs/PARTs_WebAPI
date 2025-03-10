# Generated by Django 5.1.5 on 2025-02-13 14:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0067_dashboardviewtype_remove_dashboard_reference_team_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='default_dash_view_typ',
            field=models.ForeignKey(default='main', on_delete=django.db.models.deletion.PROTECT, to='scouting.dashboardviewtype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dashboardgraph',
            name='dashboard_view',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='scouting.dashboardview'),
            preserve_default=False,
        ),
    ]
