# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.contrib.auth.models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('companies', '0001_initial'),
        ('projects', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True, max_length=30, error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active', default=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('groups', models.ManyToManyField(related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', to='auth.Group', blank=True, related_query_name='user')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', help_text='Specific permissions for this user.', verbose_name='user permissions', to='auth.Permission', blank=True, related_query_name='user')),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=30)),
                ('job_title', models.CharField(blank=True, max_length=60)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('entity', models.ForeignKey(to='companies.Entity')),
                ('section', models.ForeignKey(null=True, to='companies.Section')),
                ('tenant', models.ForeignKey(related_name='clientemployees', to='tenants.Tenant')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('user',),
                'default_related_name': 'employees',
            },
        ),
        migrations.CreateModel(
            name='ClientManager',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=30)),
                ('job_title', models.CharField(blank=True, max_length=60)),
                ('place_id', models.PositiveIntegerField(null=True, blank=True)),
                ('company', models.ForeignKey(related_name='managers', to='companies.Company')),
                ('place_type', models.ForeignKey(related_name='place_type', null=True, blank=True, to='contenttypes.ContentType')),
                ('tenant', models.ForeignKey(related_name='clientmanagers', to='tenants.Tenant')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='ClientProjectManager',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=30)),
                ('job_title', models.CharField(blank=True, max_length=60)),
                ('company', models.ForeignKey(related_name='project_managers', to='companies.Company')),
                ('tenant', models.ForeignKey(related_name='clientprojectmanagers', to='tenants.Tenant')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='PersonToAssess',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('person_id', models.PositiveIntegerField()),
                ('person_type', models.ForeignKey(related_name='content_type_person_to_assess', to='contenttypes.ContentType')),
                ('research_methodology', models.ForeignKey(related_name='people_to_assess', to='projects.ResearchMethodology')),
            ],
        ),
        migrations.CreateModel(
            name='Shopper',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(max_length=1)),
                ('has_drivers_license', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name='shopper', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TenantConsultant',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('tenant', models.ForeignKey(related_name='consultants', to='tenants.Tenant')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='TenantProductManager',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('tenant', models.ForeignKey(related_name='product_managers', to='tenants.Tenant')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='TenantProjectManager',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('tenant', models.ForeignKey(related_name='project_managers', to='tenants.Tenant')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('user',),
            },
        ),
    ]
