# Generated by Django 4.2 on 2024-02-18 00:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0017_questionaggregate_field_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='questioncondition',
            name='condition_question',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='condition_question', to='form.question'),
            preserve_default=False,
        ),
    ]
