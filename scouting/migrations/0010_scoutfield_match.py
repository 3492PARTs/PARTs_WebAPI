# Generated by Django 4.0.3 on 2023-04-21 00:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0009_teamnotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoutfield',
            name='match',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='scouting.match'),
        ),
    ]
