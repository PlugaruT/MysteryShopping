# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-31 12:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0001_initial'),
        ('companies', '0001_initial'),
        ('questionnaires', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('type', models.CharField(choices=[('m', 'Mystery Evaluation'), ('c', 'Customer Experience Index Evaluation')], default='m', max_length=1)),
                ('employee_id', models.PositiveIntegerField(blank=True, null=True)),
                ('evaluation_type', model_utils.fields.StatusField(choices=[('call', 'Call'), ('visit', 'Visit')], default='call', max_length=100, no_check_for_status=True)),
                ('is_draft', models.BooleanField(default=True)),
                ('suggested_start_date', models.DateTimeField(null=True)),
                ('suggested_end_date', models.DateTimeField(null=True)),
                ('status', model_utils.fields.StatusField(choices=[('planned', 'Planned'), ('draft', 'Draft'), ('submitted', 'Submitted'), ('reviewed', 'Reviewed'), ('approved', 'Approved'), ('declined', 'Declined'), ('rejected', 'Rejected')], default='planned', max_length=100, no_check_for_status=True)),
                ('time_accomplished', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'default_related_name': 'evaluations',
            },
        ),
        migrations.CreateModel(
            name='EvaluationAssessmentComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commenter_id', models.PositiveIntegerField()),
                ('comment', models.TextField()),
            ],
            options={
                'default_related_name': 'evaluation_assessment_comments',
            },
        ),
        migrations.CreateModel(
            name='EvaluationAssessmentLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(blank=True, default=0, null=True)),
            ],
            options={
                'ordering': ('level',),
                'default_related_name': 'evaluation_assessment_levels',
            },
        ),
        migrations.CreateModel(
            name='PlaceToAssess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_id', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('type', models.CharField(choices=[('m', 'Mystery Questionnaire'), ('c', 'Customer Experience Index Questionnaire')], default='m', max_length=1)),
                ('company', models.IntegerField()),
            ],
            options={
                'ordering': ('tenant',),
                'default_related_name': 'projects',
            },
        ),
        migrations.CreateModel(
            name='ResearchMethodology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_evaluations', models.PositiveSmallIntegerField()),
                ('description', models.TextField(blank=True)),
                ('questionnaires', models.ManyToManyField(to='questionnaires.QuestionnaireTemplate')),
                ('scripts', models.ManyToManyField(to='questionnaires.QuestionnaireScript')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
            ],
            options={
                'verbose_name_plural': 'research methodologies',
                'ordering': ('number_of_evaluations',),
                'default_related_name': 'research_methodologies',
            },
        ),
    ]
