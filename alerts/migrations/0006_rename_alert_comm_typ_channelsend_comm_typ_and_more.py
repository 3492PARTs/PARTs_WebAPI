# Generated by Django 5.1.1 on 2025-01-23 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0005_rename_alertchannelsend_channelsend_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channelsend',
            old_name='alert_comm_typ',
            new_name='comm_typ',
        ),
        migrations.RenameField(
            model_name='channelsend',
            old_name='alert_channel_send_id',
            new_name='id',
        ),
    ]
