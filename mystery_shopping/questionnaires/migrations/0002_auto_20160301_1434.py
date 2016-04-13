# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionnairequestion',
            name='answer_choices',
        ),
        migrations.AddField(
            model_name='questionnairequestion',
            name='answer_choices',
            field=django.contrib.postgres.fields.ArrayField(blank=True, base_field=models.IntegerField(), size=None, null=True),
        ),
    ]
