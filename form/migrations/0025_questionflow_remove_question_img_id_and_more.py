# Generated by Django 5.1.1 on 2025-01-14 20:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0024_questiontype_requires_img'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionFlow',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('void_ind', models.CharField(default='n', max_length=1)),
            ],
        ),
        migrations.RemoveField(
            model_name='question',
            name='img_id',
        ),
        migrations.RemoveField(
            model_name='question',
            name='img_ver',
        ),
        migrations.RemoveField(
            model_name='questiontype',
            name='requires_img',
        ),
        migrations.AddField(
            model_name='question',
            name='question_flow',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='form.questionflow'),
        ),
    ]
