# Generated by Django 5.1.5 on 2025-02-05 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0050_graphcategory_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphtype',
            name='required_graph_question_typ',
            field=models.ManyToManyField(to='form.graphquestiontype'),
        ),
    ]
