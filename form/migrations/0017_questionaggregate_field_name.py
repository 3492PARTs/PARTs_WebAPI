# Generated by Django 4.2 on 2024-02-17 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0016_questionaggregate_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionaggregate',
            name='field_name',
            field=models.CharField(default=' ', max_length=1000),
            preserve_default=False,
        ),
    ]
