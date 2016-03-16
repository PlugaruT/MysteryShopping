# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0003_auto_20160316_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='type',
            field=models.CharField(default='m', choices=[('m', 'Mystery Questionnaire'), ('n', 'NPS Questionnaire')], max_length=1),
        ),
        migrations.AddField(
            model_name='questionnairetemplate',
            name='type',
            field=models.CharField(default='m', choices=[('m', 'Mystery Questionnaire'), ('n', 'NPS Questionnaire')], max_length=1),
        ),
    ]
