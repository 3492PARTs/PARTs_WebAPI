# Generated by Django 3.0.6 on 2020-05-18 01:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authAPI', '0004_auto_20200518_0050'),
    ]

    operations = [
        migrations.RenameField(
            model_name='errorlog',
            old_name='method',
            new_name='path',
        ),
        migrations.RemoveField(
            model_name='errorlog',
            name='app',
        ),
        migrations.RemoveField(
            model_name='errorlog',
            name='controller',
        ),
    ]
