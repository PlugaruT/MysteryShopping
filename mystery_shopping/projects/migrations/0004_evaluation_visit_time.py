# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-10 06:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20160616_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='visit_time',
            field=models.DateField(null=True),
        ),
    ]
