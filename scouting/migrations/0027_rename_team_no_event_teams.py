# Generated by Django 5.0.3 on 2024-05-21 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0026_alter_userinfo_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='team_no',
            new_name='teams',
        ),
    ]