# Generated by Django 4.0.3 on 2023-04-29 19:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_userpushnotificationsubscriptionobjects'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpushnotificationsubscriptionobjects',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
