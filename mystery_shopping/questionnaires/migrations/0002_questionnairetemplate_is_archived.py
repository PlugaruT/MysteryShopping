# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-05 09:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnairetemplate',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]
