# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-18 13:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0006_company_subindustry'),
        ('cxi', '0007_auto_20160916_0659'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectcomment',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Department'),
        ),
        migrations.AddField(
            model_name='projectcomment',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Section'),
        ),
    ]
