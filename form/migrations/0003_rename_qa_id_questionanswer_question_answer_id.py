# Generated by Django 4.2 on 2023-06-30 00:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0002_rename_q_id_question_question_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionanswer',
            old_name='qa_id',
            new_name='question_answer_id',
        ),
    ]