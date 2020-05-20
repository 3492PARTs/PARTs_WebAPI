# Generated by Django 3.0.6 on 2020-05-14 17:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('description', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codename', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthtokenToken',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('created', models.DateTimeField()),
            ],
            options={
                'db_table': 'authtoken_token',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(blank=True, max_length=128, null=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.IntegerField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('email', models.CharField(blank=True, max_length=254, null=True)),
                ('first_name', models.CharField(blank=True, max_length=20, null=True)),
                ('last_name', models.CharField(blank=True, max_length=150, null=True)),
                ('is_staff', models.IntegerField(blank=True, null=True)),
                ('is_active', models.IntegerField(blank=True, null=True)),
                ('date_joined', models.DateTimeField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField(blank=True, null=True)),
                ('object_id', models.TextField(blank=True, null=True)),
                ('object_repr', models.CharField(blank=True, max_length=200, null=True)),
                ('change_message', models.TextField(blank=True, null=True)),
                ('action_flag', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(blank=True, max_length=100, null=True)),
                ('model', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('app', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('applied', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=40, null=True, unique=True)),
                ('session_data', models.TextField(blank=True, null=True)),
                ('expire_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'django_session',
                'managed': False,
            },
        ),
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
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('error_log_id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.CharField(blank=True, max_length=1000, null=True)),
                ('exception', models.CharField(blank=True, max_length=4000, null=True)),
                ('time', models.DateTimeField()),
                ('void_ind', models.CharField(default='n', max_length=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]