# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0006_auto_20160322_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnairetemplatequestion',
            name='show_comment',
            field=models.BooleanField(default=True),
        ),
    ]
