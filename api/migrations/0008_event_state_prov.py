# Generated by Django 4.0.1 on 2022-03-15 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_event_webcast_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='state_prov',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
