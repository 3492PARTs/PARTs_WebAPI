# Generated by Django 4.0.3 on 2023-04-29 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0010_scoutfield_match'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoutquestion',
            name='void_ind',
            field=models.CharField(default='n', max_length=1),
        ),
    ]
