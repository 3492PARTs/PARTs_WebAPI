# Generated by Django 5.1.5 on 2025-02-05 20:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0051_graphtype_required_graph_question_typ'),
    ]

    operations = [
        migrations.RenameField(
            model_name='graphtype',
            old_name='required_graph_question_typ',
            new_name='requires_graph_question_typs',
        ),
    ]
