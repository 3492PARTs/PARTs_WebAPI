# Generated by Django 5.1.5 on 2025-02-09 03:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0059_graph'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('active', models.CharField(default='y', max_length=1)),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.season')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DashboardGraph',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order', models.IntegerField()),
                ('active', models.CharField(default='y', max_length=1)),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.dashboard')),
                ('graph', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.graph')),
            ],
        ),
    ]
