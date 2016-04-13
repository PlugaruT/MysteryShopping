# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='questionnaire_script',
            field=models.ForeignKey(null=True, to='questionnaires.QuestionnaireScript'),
        ),
    ]
