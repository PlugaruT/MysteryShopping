# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-17 08:13
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0010_auto_20170105_1010'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='companyelement',
            managers=[
                ('tree', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelOptions(
            name='companyelement',
            options={'permissions': (('view_companyelement', 'View company element'), ('view_detractors_for_companyelement', 'View detractors for company element'), ('view_statistics_for_companyelement', 'View statistics for company element'), ('view_coded_causes_for_companyelement', 'View detractors for company element'))},
        ),
    ]
