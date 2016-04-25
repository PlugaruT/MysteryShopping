# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-16 13:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0008_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrossIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=40)),
                ('score', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
            ],
            options={
                'default_related_name': 'cross_indexes',
            },
        ),
        migrations.CreateModel(
            name='CrossIndexTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=40)),
                ('question_templates', models.ManyToManyField(to='questionnaires.QuestionnaireTemplateQuestion')),
                ('questionnaire_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaires.QuestionnaireTemplate')),
            ],
            options={
                'default_related_name': 'cross_index_templates',
            },
        ),
        migrations.AlterModelManagers(
            name='questionnaireblock',
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='questionnairetemplateblock',
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='crossindex',
            name='cross_index_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaires.CrossIndexTemplate'),
        ),
        migrations.AddField(
            model_name='crossindex',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaires.Questionnaire'),
        ),
        migrations.AddField(
            model_name='crossindex',
            name='questions',
            field=models.ManyToManyField(to='questionnaires.QuestionnaireQuestion'),
        ),
    ]
