# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-12 10:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_company_contact_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='subindustry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.SubIndustry'),
        ),
    ]
