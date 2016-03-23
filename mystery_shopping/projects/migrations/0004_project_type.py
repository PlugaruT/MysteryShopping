# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20160322_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='type',
            field=models.CharField(default='m', choices=[('m', 'Mystery Questionnaire'), ('c', 'Customer Experience Index Questionnaire')], max_length=1),
        ),
    ]
