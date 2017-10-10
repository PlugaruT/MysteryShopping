# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-10 13:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20171010_1623'),
        ('cxi', '0010_auto_20171010_1623'),
        ('dashboard', '0006_remove_dashboardtemplate_company'),
        ('companies', '0012_auto_20170118_1605'),
    ]

    operations = [
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
            name='company',
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
