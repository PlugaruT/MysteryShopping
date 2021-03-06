# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-03 14:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_detractorrespondent_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='detractorrespondent',
            name='additional_comment',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AddField(
            model_name='detractorrespondent',
            name='status',
            field=models.CharField(choices=[('TO_CONTACT', 'To Contact'), ('CALL_BACK', 'Call Back'), ('CONTACTED', 'Contacted')], default='TO_CONTACT', max_length=11),
        ),
    ]
