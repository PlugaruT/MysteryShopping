# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-09 18:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_subindustry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subindustry',
            name='industry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subindustry', to='companies.Industry'),
        ),
    ]
