# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-13 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20160909_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industry',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='subindustry',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]