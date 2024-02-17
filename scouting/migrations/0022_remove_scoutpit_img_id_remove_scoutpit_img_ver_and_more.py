# Generated by Django 4.2 on 2024-02-15 00:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0013_remove_question_season_and_more'),
        ('scouting', '0021_remove_question_question_id_tmp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scoutpit',
            name='img_id',
        ),
        migrations.RemoveField(
            model_name='scoutpit',
            name='img_ver',
        ),
        migrations.AlterField(
            model_name='scoutpit',
            name='response',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='form.response'),
        ),
        migrations.CreateModel(
            name='ScoutPitImage',
            fields=[
                ('scout_pit_img_id', models.AutoField(primary_key=True, serialize=False)),
                ('img_id', models.CharField(blank=True, max_length=500, null=True)),
                ('img_ver', models.CharField(blank=True, max_length=500, null=True)),
                ('scout_pit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scouting.scoutpit')),
            ],
        ),
    ]