# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-15 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0007_auto_20160914_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnairequestion',
            name='question_body',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='questionnairetemplatequestion',
            name='question_body',
            field=models.TextField(),
        ),
    ]
