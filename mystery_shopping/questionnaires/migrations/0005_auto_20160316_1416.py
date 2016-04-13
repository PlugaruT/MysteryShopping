# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0004_auto_20160316_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='created',
            field=model_utils.fields.AutoCreatedField(editable=False, default=django.utils.timezone.now, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(editable=False, default=django.utils.timezone.now, verbose_name='modified'),
        ),
    ]
