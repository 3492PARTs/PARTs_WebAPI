# Generated by Django 5.1.1 on 2025-01-15 21:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0026_questionflow_form_sub_typ_questionflow_form_typ'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswer',
            name='question_flow',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='form.questionflow'),
        ),
        migrations.AlterField(
            model_name='questionanswer',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='form.question'),
        ),
        migrations.CreateModel(
            name='QuestionFlowAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('answer', models.TextField(blank=True, null=True)),
                ('answer_time', models.TimeField(blank=True, null=True)),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='form.question')),
                ('question_answer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='form.questionanswer')),
            ],
        ),
    ]
