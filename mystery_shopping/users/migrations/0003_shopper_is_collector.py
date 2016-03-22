# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_collector'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopper',
            name='is_collector',
            field=models.BooleanField(default=False),
        ),
    ]
