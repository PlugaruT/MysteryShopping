# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-31 12:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0001_initial'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.Entity')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
            ],
            options={
                'ordering': ('entity', 'name'),
                'default_related_name': 'sections',
            },
        ),
        migrations.AddField(
            model_name='company',
            name='industry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.Industry'),
        ),
        migrations.AddField(
            model_name='company',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant'),
        ),
    ]
