# Generated by Django 5.1.1 on 2024-11-01 00:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('user', '0007_user_img_id_user_img_ver_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('link_id', models.AutoField(primary_key=True, serialize=False)),
                ('menu_name', models.CharField(max_length=255)),
                ('routerlink', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth.permission')),
            ],
        ),
        migrations.DeleteModel(
            name='UserLinks',
        ),
    ]
