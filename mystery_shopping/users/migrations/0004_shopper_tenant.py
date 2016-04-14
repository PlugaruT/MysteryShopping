# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
        ('users', '0003_shopper_is_collector'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopper',
            name='tenant',
            field=models.ForeignKey(blank=True, to='tenants.Tenant', null=True, related_name='shoppers'),
        ),
    ]
