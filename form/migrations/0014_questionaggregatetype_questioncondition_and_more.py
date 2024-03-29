# Generated by Django 4.2 on 2024-02-16 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0013_remove_question_season_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionAggregateType',
            fields=[
                ('question_aggregate_typ', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('question_aggregate_nm', models.CharField(max_length=255)),
                ('void_ind', models.CharField(default='n', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionCondition',
            fields=[
                ('question_condition_id', models.AutoField(primary_key=True, serialize=False)),
                ('condition', models.CharField(max_length=1000)),
                ('active', models.CharField(default='y', max_length=1)),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='form.question')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionAggregate',
            fields=[
                ('question_aggregate_id', models.AutoField(primary_key=True, serialize=False)),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('question', models.ManyToManyField(to='form.question')),
                ('question_aggregate_typ', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='form.questionaggregatetype')),
            ],
        ),
    ]
