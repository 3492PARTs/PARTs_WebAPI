# Generated by Django 5.1.1 on 2024-11-29 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_errorlog_traceback'),
    ]

    operations = [
        migrations.AddField(
            model_name='errorlog',
            name='error_message',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
    ]