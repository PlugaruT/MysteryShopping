# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0002_auto_20160301_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnairequestion',
            name='type',
            field=models.CharField(max_length=1, choices=[('t', 'Text Field'), ('d', 'Date Field'), ('s', 'Single Choice'), ('m', 'Multiple Choice'), ('n', 'NPS')], default='t'),
        ),
        migrations.AlterField(
            model_name='questionnairetemplatequestion',
            name='type',
            field=models.CharField(max_length=1, choices=[('t', 'Text Field'), ('d', 'Date Field'), ('s', 'Single Choice'), ('m', 'Multiple Choice'), ('n', 'NPS')], default='t'),
        ),
    ]
