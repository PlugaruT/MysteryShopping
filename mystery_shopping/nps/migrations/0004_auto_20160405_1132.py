# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nps', '0003_auto_20160331_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='codedcause',
            name='sentiment',
            field=models.CharField(max_length=1, choices=[('a', 'Appreciation'), ('f', 'Frustration')], default='a'),
        ),
        migrations.AlterField(
            model_name='codedcause',
            name='type',
            field=models.CharField(max_length=1, choices=[('n', 'NPS questions'), ('j', 'Enjoyability questions'), ('e', 'Easiness questions'), ('u', 'Usefulness questions')], default='n'),
        ),
    ]
