# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-12 06:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0012_auto_20170721_1354'),
    ]

    db_operations = [
        migrations.AlterModelTable(name='DetractorRespondent', table='respondents_respondent')
    ]

    state_operations = [
        migrations.DeleteModel(name='DetractorRespondent'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(database_operations=db_operations, state_operations=state_operations)
    ]
