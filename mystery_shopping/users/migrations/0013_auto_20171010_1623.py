# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-10 13:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20170721_1354'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persontoassess',
            name='person_type',
        ),
        migrations.RemoveField(
            model_name='persontoassess',
            name='research_methodology',
        ),
    ]
