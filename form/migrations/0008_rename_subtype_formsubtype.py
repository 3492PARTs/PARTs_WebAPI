# Generated by Django 4.2 on 2023-07-14 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0007_rename_type_formtype'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SubType',
            new_name='FormSubType',
        ),
    ]
