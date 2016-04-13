# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0006_auto_20160322_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodedCause',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('cause_type', models.CharField(choices=[('n', 'n'), ('NPS questions', 'NPS questions'), ('j', 'j'), ('Enjoyability questions', 'Enjoyability questions'), ('e', 'e'), ('Easiness questions', 'Easiness questions'), ('u', 'u'), ('Usefulness questions', 'Usefulness questions')], default='n', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='CodedCauseLabel',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='codedcause',
            name='coded_label',
            field=models.ForeignKey(to='nps.CodedCauseLabel'),
        ),
        migrations.AddField(
            model_name='codedcause',
            name='parent',
            field=models.ForeignKey(to='nps.CodedCause', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='codedcause',
            name='raw_causes',
            field=models.ManyToManyField(to='questionnaires.QuestionnaireQuestion'),
        ),
    ]
