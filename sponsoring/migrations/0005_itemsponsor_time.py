# Generated by Django 4.2 on 2023-07-28 23:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sponsoring', '0004_itemsponsor_void_ind'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemsponsor',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]