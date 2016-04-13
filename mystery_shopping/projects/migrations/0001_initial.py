# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        ('questionnaires', '0001_initial'),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(editable=False, default=django.utils.timezone.now, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(editable=False, default=django.utils.timezone.now, verbose_name='modified')),
                ('employee_id', models.PositiveIntegerField(null=True, blank=True)),
                ('evaluation_type', model_utils.fields.StatusField(default='call', no_check_for_status=True, max_length=100, choices=[('call', 'Call'), ('visit', 'Visit')])),
                ('is_draft', models.BooleanField(default=True)),
                ('suggested_start_date', models.DateTimeField(null=True)),
                ('suggested_end_date', models.DateTimeField(null=True)),
                ('status', model_utils.fields.StatusField(default='planned', no_check_for_status=True, max_length=100, choices=[('planned', 'Planned'), ('draft', 'Draft'), ('submitted', 'Submitted'), ('reviewed', 'Reviewed'), ('approved', 'Approved'), ('declined', 'Declined'), ('rejected', 'Rejected')])),
                ('time_accomplished', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'default_related_name': 'evaluations',
            },
        ),
        migrations.CreateModel(
            name='EvaluationAssessmentComment',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('level', models.PositiveIntegerField(null=True, default=0, blank=True)),
            ],
            options={
                'ordering': ('level',),
                'default_related_name': 'evaluation_assessment_levels',
            },
        ),
        migrations.CreateModel(
            name='PlaceToAssess',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('place_id', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('company', models.ForeignKey(to='companies.Company')),
            ],
            options={
                'ordering': ('tenant',),
                'default_related_name': 'projects',
            },
        ),
        migrations.CreateModel(
            name='ResearchMethodology',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('number_of_evaluations', models.PositiveSmallIntegerField()),
                ('description', models.TextField(blank=True)),
                ('questionnaires', models.ManyToManyField(to='questionnaires.QuestionnaireTemplate')),
                ('scripts', models.ManyToManyField(to='questionnaires.QuestionnaireScript')),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
            ],
            options={
                'verbose_name_plural': 'research methodologies',
                'ordering': ('number_of_evaluations',),
                'default_related_name': 'research_methodologies',
            },
        ),
    ]
