# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('users', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('questionnaires', '0001_initial'),
        ('tenants', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='consultants',
            field=models.ManyToManyField(to='users.TenantConsultant'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_manager',
            field=models.ForeignKey(to='users.TenantProjectManager'),
        ),
        migrations.AddField(
            model_name='project',
            name='research_methodology',
            field=models.ForeignKey(null=True, blank=True, to='projects.ResearchMethodology'),
        ),
        migrations.AddField(
            model_name='project',
            name='shoppers',
            field=models.ManyToManyField(to='users.Shopper'),
        ),
        migrations.AddField(
            model_name='project',
            name='tenant',
            field=models.ForeignKey(to='tenants.Tenant'),
        ),
        migrations.AddField(
            model_name='placetoassess',
            name='place_type',
            field=models.ForeignKey(to='contenttypes.ContentType', related_name='content_type_place_to_assess'),
        ),
        migrations.AddField(
            model_name='placetoassess',
            name='research_methodology',
            field=models.ForeignKey(to='projects.ResearchMethodology', related_name='places_to_assess'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentlevel',
            name='consultants',
            field=models.ManyToManyField(to='users.TenantConsultant'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentlevel',
            name='previous_level',
            field=models.OneToOneField(null=True, related_name='next_level', blank=True, to='projects.EvaluationAssessmentLevel'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentlevel',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentlevel',
            name='project_manager',
            field=models.ForeignKey(null=True, to='users.TenantProjectManager'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentcomment',
            name='commenter_type',
            field=models.ForeignKey(to='contenttypes.ContentType', related_name='commenter_type'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentcomment',
            name='evaluation',
            field=models.ForeignKey(to='projects.Evaluation'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentcomment',
            name='evaluation_assessment_level',
            field=models.ForeignKey(to='projects.EvaluationAssessmentLevel'),
        ),
        migrations.AddField(
            model_name='evaluationassessmentcomment',
            name='questionnaire',
            field=models.ForeignKey(to='questionnaires.Questionnaire'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='employee_type',
            field=models.ForeignKey(null=True, blank=True, related_name='employee_type', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='entity',
            field=models.ForeignKey(to='companies.Entity'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='evaluation_assessment_level',
            field=models.ForeignKey(null=True, blank=True, to='projects.EvaluationAssessmentLevel'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='questionnaire',
            field=models.OneToOneField(null=True, blank=True, to='questionnaires.Questionnaire'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='questionnaire_script',
            field=models.ForeignKey(to='questionnaires.QuestionnaireScript'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='questionnaire_template',
            field=models.ForeignKey(to='questionnaires.QuestionnaireTemplate'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='section',
            field=models.ForeignKey(null=True, blank=True, to='companies.Section'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='shopper',
            field=models.ForeignKey(to='users.Shopper'),
        ),
    ]
