# Generated by Django 4.2 on 2023-07-14 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0006_question_required'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Type',
            new_name='FormType',
        ),
    ]