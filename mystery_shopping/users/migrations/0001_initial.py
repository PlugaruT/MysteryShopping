# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('companies', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
        ('projects', '0001_initial'),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(unique=True, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], max_length=30, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=20, blank=True)),
                ('groups', models.ManyToManyField(blank=True, verbose_name='groups', related_name='user_set', to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(blank=True, verbose_name='user permissions', related_name='user_set', to='auth.Permission', help_text='Specific permissions for this user.', related_query_name='user')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ClientEmployee',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('first_name', models.CharField(max_length=30, blank=True)),
                ('last_name', models.CharField(max_length=30, blank=True)),
                ('job_title', models.CharField(max_length=60, blank=True)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('entity', models.ForeignKey(to='companies.Entity')),
                ('section', models.ForeignKey(null=True, to='companies.Section')),
                ('tenant', models.ForeignKey(to='tenants.Tenant', related_name='clientemployees')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
                'default_related_name': 'employees',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientManager',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('first_name', models.CharField(max_length=30, blank=True)),
                ('last_name', models.CharField(max_length=30, blank=True)),
                ('job_title', models.CharField(max_length=60, blank=True)),
                ('place_id', models.PositiveIntegerField(null=True, blank=True)),
                ('company', models.ForeignKey(to='companies.Company', related_name='managers')),
                ('place_type', models.ForeignKey(null=True, blank=True, related_name='place_type', to='contenttypes.ContentType')),
                ('tenant', models.ForeignKey(to='tenants.Tenant', related_name='clientmanagers')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientProjectManager',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('first_name', models.CharField(max_length=30, blank=True)),
                ('last_name', models.CharField(max_length=30, blank=True)),
                ('job_title', models.CharField(max_length=60, blank=True)),
                ('company', models.ForeignKey(to='companies.Company', related_name='project_managers')),
                ('tenant', models.ForeignKey(to='tenants.Tenant', related_name='clientprojectmanagers')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonToAssess',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('person_id', models.PositiveIntegerField()),
                ('person_type', models.ForeignKey(to='contenttypes.ContentType', related_name='content_type_person_to_assess')),
                ('research_methodology', models.ForeignKey(to='projects.ResearchMethodology', related_name='people_to_assess')),
            ],
        ),
        migrations.CreateModel(
            name='Shopper',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(max_length=1)),
                ('has_drivers_license', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name='shopper', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TenantConsultant',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('tenant', models.ForeignKey(to='tenants.Tenant', related_name='consultants')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TenantProductManager',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('tenant', models.ForeignKey(to='tenants.Tenant', related_name='product_managers')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TenantProjectManager',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('tenant', models.ForeignKey(to='tenants.Tenant', related_name='project_managers')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
                'abstract': False,
            },
        ),
    ]
