# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('score', models.DecimalField(decimal_places=2, null=True, max_digits=5)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                'default_related_name': 'questionnaires',
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('order', models.PositiveIntegerField()),
                ('score', models.DecimalField(decimal_places=2, null=True, max_digits=5)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent_block', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='children', to='questionnaires.QuestionnaireBlock')),
                ('questionnaire', models.ForeignKey(to='questionnaires.Questionnaire', related_name='blocks')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('question_body', models.CharField(max_length=200)),
                ('type', models.CharField(default='t', max_length=1, choices=[('t', 'Text Field'), ('d', 'Date Field'), ('s', 'Single Choice'), ('m', 'Multiple Choice')])),
                ('max_score', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('order', models.PositiveIntegerField()),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('score', models.DecimalField(null=True, decimal_places=2, blank=True, max_digits=5)),
                ('answer', models.TextField(null=True, blank=True)),
                ('show_comment', models.BooleanField(default=True)),
                ('comment', models.TextField(null=True, blank=True)),
            ],
            options={
                'default_related_name': 'questions',
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireQuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('text', models.CharField(max_length=255, null=True)),
                ('score', models.DecimalField(decimal_places=2, null=True, max_digits=5)),
                ('weight', models.DecimalField(decimal_places=2, null=True, max_digits=5)),
                ('order', models.PositiveIntegerField()),
                ('question', models.ForeignKey(to='questionnaires.QuestionnaireQuestion')),
            ],
            options={
                'default_related_name': 'question_choices',
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireScript',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('is_editable', models.BooleanField(default=True)),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireTemplateBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('order', models.PositiveIntegerField()),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent_block', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='children', to='questionnaires.QuestionnaireTemplateBlock')),
                ('questionnaire_template', models.ForeignKey(to='questionnaires.QuestionnaireTemplate', related_name='template_blocks')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireTemplateQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('question_body', models.CharField(max_length=200)),
                ('type', models.CharField(default='t', max_length=1, choices=[('t', 'Text Field'), ('d', 'Date Field'), ('s', 'Single Choice'), ('m', 'Multiple Choice')])),
                ('max_score', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('order', models.PositiveIntegerField()),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('questionnaire_template', models.ForeignKey(to='questionnaires.QuestionnaireTemplate')),
                ('template_block', models.ForeignKey(to='questionnaires.QuestionnaireTemplateBlock')),
            ],
            options={
                'default_related_name': 'template_questions',
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireTemplateQuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('text', models.CharField(max_length=255, null=True)),
                ('score', models.DecimalField(decimal_places=2, null=True, max_digits=5)),
                ('weight', models.DecimalField(decimal_places=2, null=True, max_digits=5)),
                ('order', models.PositiveIntegerField()),
                ('template_question', models.ForeignKey(to='questionnaires.QuestionnaireTemplateQuestion')),
            ],
            options={
                'default_related_name': 'template_question_choices',
            },
        ),
        migrations.AddField(
            model_name='questionnairequestion',
            name='answer_choices',
            field=models.ManyToManyField(blank=True, to='questionnaires.QuestionnaireQuestionChoice'),
        ),
        migrations.AddField(
            model_name='questionnairequestion',
            name='block',
            field=models.ForeignKey(to='questionnaires.QuestionnaireBlock'),
        ),
        migrations.AddField(
            model_name='questionnairequestion',
            name='questionnaire',
            field=models.ForeignKey(to='questionnaires.Questionnaire'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='template',
            field=models.ForeignKey(to='questionnaires.QuestionnaireTemplate'),
        ),
    ]
