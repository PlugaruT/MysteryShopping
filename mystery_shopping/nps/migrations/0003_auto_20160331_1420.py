# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
        ('nps', '0002_auto_20160330_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='codedcause',
            name='tenant',
            field=models.ForeignKey(default=1, to='tenants.Tenant'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='codedcauselabel',
            name='tenant',
            field=models.ForeignKey(default=1, to='tenants.Tenant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='codedcause',
            name='raw_causes',
            field=models.ManyToManyField(related_name='coded_causes', to='questionnaires.QuestionnaireQuestion'),
        ),
    ]
