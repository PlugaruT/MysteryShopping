# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0005_auto_20160316_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='type',
            field=models.CharField(max_length=1, default='m', choices=[('m', 'Mystery Questionnaire'), ('c', 'Customer Experience Index Questionnaire')]),
        ),
        migrations.AlterField(
            model_name='questionnairetemplate',
            name='type',
            field=models.CharField(max_length=1, default='m', choices=[('m', 'Mystery Questionnaire'), ('c', 'Customer Experience Index Questionnaire')]),
        ),
    ]
