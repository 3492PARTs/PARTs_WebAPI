# Generated by Django 4.2 on 2024-02-15 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0023_scoutpitimage_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoutpitimage',
            name='void_ind',
            field=models.CharField(default='n', max_length=1),
        ),
    ]
