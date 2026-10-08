from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0065_flow_form_based'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_flow',
            field=models.ManyToManyField(blank=True, to='form.flow'),
        ),
    ]
