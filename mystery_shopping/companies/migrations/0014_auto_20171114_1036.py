# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-11-14 08:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cxi', '0011_auto_20171114_1036'),
        ('companies', '0013_auto_20171010_1623'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='company',
            name='country',
        ),
        migrations.RemoveField(
            model_name='company',
            name='industry',
        ),
        migrations.RemoveField(
            model_name='company',
            name='subindustry',
        ),
        migrations.RemoveField(
            model_name='company',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='department',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='entity',
            name='city',
        ),
        migrations.RemoveField(
            model_name='entity',
            name='department',
        ),
        migrations.RemoveField(
            model_name='entity',
            name='sector',
        ),
        migrations.RemoveField(
            model_name='entity',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='section',
            name='entity',
        ),
        migrations.RemoveField(
            model_name='section',
            name='tenant',
        ),
        migrations.DeleteModel(
            name='Company',
        ),
        migrations.DeleteModel(
            name='Department',
        ),
        migrations.DeleteModel(
            name='Entity',
        ),
        migrations.DeleteModel(
            name='Section',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
