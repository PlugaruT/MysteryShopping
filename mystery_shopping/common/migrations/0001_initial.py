# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('zip_code', models.CharField(max_length=10, blank=True)),
            ],
            options={
                'verbose_name_plural': 'cities',
                'ordering': ('county', 'name'),
                'default_related_name': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name_plural': 'countries',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CountryRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('country', models.ForeignKey(to='common.Country')),
            ],
            options={
                'ordering': ('name',),
                'default_related_name': 'regions',
            },
        ),
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('country', models.ForeignKey(to='common.Country')),
                ('country_region', models.ForeignKey(to='common.CountryRegion')),
            ],
            options={
                'verbose_name_plural': 'counties',
                'ordering': ('name',),
                'default_related_name': 'counties',
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('city', models.ForeignKey(to='common.City')),
            ],
            options={
                'ordering': ('city', 'name'),
                'default_related_name': 'sectors',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='county',
            field=models.ForeignKey(to='common.County'),
        ),
    ]
