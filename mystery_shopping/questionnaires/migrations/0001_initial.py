# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('score', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                'default_related_name': 'questionnaires',
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireBlock',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=50)),
                ('weight', models.DecimalField(max_digits=5, decimal_places=2)),
                ('order', models.PositiveIntegerField()),
                ('score', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent_block', mptt.fields.TreeForeignKey(related_name='children', null=True, blank=True, to='questionnaires.QuestionnaireBlock')),
                ('questionnaire', models.ForeignKey(related_name='blocks', to='questionnaires.Questionnaire')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireQuestion',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('question_body', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('t', 'Text Field'), ('d', 'Date Field'), ('s', 'Single Choice'), ('m', 'Multiple Choice')], max_length=1, default='t')),
                ('max_score', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('order', models.PositiveIntegerField()),
                ('weight', models.DecimalField(max_digits=5, decimal_places=2)),
                ('score', models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=5)),
                ('answer', models.TextField(null=True, blank=True)),
                ('show_comment', models.BooleanField(default=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('answer_choices', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, size=None)),
                ('block', models.ForeignKey(to='questionnaires.QuestionnaireBlock')),
                ('questionnaire', models.ForeignKey(to='questionnaires.Questionnaire')),
            ],
            options={
                'default_related_name': 'questions',
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireQuestionChoice',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('text', models.CharField(null=True, max_length=255)),
                ('score', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('weight', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('is_editable', models.BooleanField(default=True)),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireTemplateBlock',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=50)),
                ('weight', models.DecimalField(max_digits=5, decimal_places=2)),
                ('order', models.PositiveIntegerField()),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent_block', mptt.fields.TreeForeignKey(related_name='children', null=True, blank=True, to='questionnaires.QuestionnaireTemplateBlock')),
                ('questionnaire_template', models.ForeignKey(related_name='template_blocks', to='questionnaires.QuestionnaireTemplate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireTemplateQuestion',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('question_body', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('t', 'Text Field'), ('d', 'Date Field'), ('s', 'Single Choice'), ('m', 'Multiple Choice')], max_length=1, default='t')),
                ('max_score', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('order', models.PositiveIntegerField()),
                ('weight', models.DecimalField(max_digits=5, decimal_places=2)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('text', models.CharField(null=True, max_length=255)),
                ('score', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('weight', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('order', models.PositiveIntegerField()),
                ('template_question', models.ForeignKey(to='questionnaires.QuestionnaireTemplateQuestion')),
            ],
            options={
                'default_related_name': 'template_question_choices',
            },
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='template',
            field=models.ForeignKey(to='questionnaires.QuestionnaireTemplate'),
        ),
    ]
