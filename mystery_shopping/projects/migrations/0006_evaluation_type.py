# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20160325_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='type',
            field=models.CharField(max_length=1, choices=[('m', 'Mystery Evaluation'), ('c', 'Customer Experience Index Evaluation')], default='m'),
        ),
    ]
