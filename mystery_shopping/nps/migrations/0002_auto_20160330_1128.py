# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nps', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='codedcause',
            old_name='cause_type',
            new_name='type',
        ),
    ]
