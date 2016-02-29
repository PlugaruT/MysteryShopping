# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('contact_person', models.CharField(max_length=100)),
                ('contact_phone', models.CharField(max_length=20)),
                ('contact_email', models.EmailField(max_length=50)),
                ('domain', models.CharField(max_length=30, verbose_name='the domain of the company on the platform')),
                ('logo', models.ImageField(null=True, blank=True, upload_to='')),
                ('country', models.ForeignKey(to='common.Country')),
            ],
            options={
                'verbose_name_plural': 'companies',
                'ordering': ('name',),
                'default_related_name': 'companies',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
            ],
            options={
                'ordering': ('company', 'name'),
                'default_related_name': 'departments',
            },
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('coordinates', models.CharField(null=True, blank=True, max_length=50)),
                ('city', models.ForeignKey(to='common.City')),
                ('department', models.ForeignKey(to='companies.Department')),
                ('sector', models.ForeignKey(null=True, to='common.Sector')),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
            ],
            options={
                'verbose_name_plural': 'entities',
                'ordering': ('department', 'name'),
                'default_related_name': 'entities',
            },
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'industries',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('entity', models.ForeignKey(to='companies.Entity')),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
            ],
            options={
                'ordering': ('entity', 'name'),
                'default_related_name': 'sections',
            },
        ),
        migrations.AddField(
            model_name='company',
            name='industry',
            field=models.ForeignKey(to='companies.Industry'),
        ),
        migrations.AddField(
            model_name='company',
            name='tenant',
            field=models.ForeignKey(to='tenants.Tenant'),
        ),
    ]
