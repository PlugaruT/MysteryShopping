# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20160229_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='questionnaire',
            field=models.OneToOneField(blank=True, related_name='evaluation', null=True, to='questionnaires.Questionnaire'),
        ),
    ]
