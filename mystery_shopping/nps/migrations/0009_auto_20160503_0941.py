# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nps', '0008_auto_20160426_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcomment',
            name='indicator',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]