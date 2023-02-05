# Generated by Django 4.0.3 on 2022-04-06 06:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=60, unique=True)),
                ('username', models.CharField(max_length=30, unique=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(default=None)),
                ('is_active', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=10, null=True)),
                ('phone_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='user.phonetype')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]