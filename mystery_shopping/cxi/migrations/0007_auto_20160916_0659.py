# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-16 06:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cxi', '0006_auto_20160915_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codedcauselabel',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
