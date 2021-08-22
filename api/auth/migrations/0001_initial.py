# Generated by Django 3.2.5 on 2021-07-18 17:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneType',
            fields=[
                ('phone_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('carrier', models.CharField(max_length=255)),
                ('phone_type', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=10, null=True)),
                ('phone_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='authAPI.phonetype')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserLinks',
            fields=[
                ('user_links_id', models.AutoField(primary_key=True, serialize=False)),
                ('menu_name', models.CharField(max_length=255)),
                ('routerlink', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth.permission')),
            ],
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('error_log_id', models.AutoField(primary_key=True, serialize=False)),
                ('path', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.CharField(blank=True, max_length=1000, null=True)),
                ('exception', models.CharField(blank=True, max_length=4000, null=True)),
                ('time', models.DateTimeField()),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
