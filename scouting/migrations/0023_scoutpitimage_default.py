# Generated by Django 4.2 on 2024-02-15 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouting', '0022_remove_scoutpit_img_id_remove_scoutpit_img_ver_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoutpitimage',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
