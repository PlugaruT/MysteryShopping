# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-28 22:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0011_customweight'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnairetemplatequestion',
            name='new_algorithm',
            field=models.BooleanField(default=True),
        ),
    ]
