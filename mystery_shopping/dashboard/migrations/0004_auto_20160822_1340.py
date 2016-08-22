# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-22 13:40
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0001_initial'),
        ('dashboard', '0003_dashboardtemplate_published'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dashboardtemplate',
            old_name='published',
            new_name='is_published',
        ),
        migrations.RemoveField(
            model_name='dashboardtemplate',
            name='project',
        ),
        migrations.AddField(
            model_name='dashboardtemplate',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dashboardtemplate',
            name='modified_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dashboardtemplate',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
