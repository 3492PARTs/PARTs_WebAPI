# Generated by Django 4.0.3 on 2022-04-06 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_user_groups_user_user_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
