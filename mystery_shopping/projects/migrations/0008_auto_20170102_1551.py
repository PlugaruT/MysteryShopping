# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-02 15:51
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection


class ResearchMethodologyReassign:
    def __init__(self, research_methodology, CompanyElement, db_alias):
        self.research_methodology = research_methodology
        self.reassign()
        self.objects = CompanyElement.objects.using(db_alias)

    def add_section_to_research_methodology(self, place_to_assess):
        try:
            company_element = self.objects.get(additional_info__old_section_id=place_to_assess.place_id)
            self.research_methodology.company_elements.add(company_element)
        except:
            pass

    def add_entity_to_research_methodology(self, place_to_assess):
        try:
            company_element = self.objects.get(additional_info__old_entity_id=place_to_assess.place_id)
            self.research_methodology.company_elements.add(company_element)
        except:
            pass

    def add_department_to_research_methodology(self, place_to_assess):
        try:
            company_element = self.objects.get(additional_info__old_department_id=place_to_assess.place_id)
            self.research_methodology.company_elements.add(company_element)
        except:
            pass

    def reassign(self):
        for place_to_assess in self.research_methodology.places_to_assess.all():
            if place_to_assess.place_type.model_class() == ContentType(app_label='companies',
                                                                       model='section').model_class():
                self.add_section_to_research_methodology(place_to_assess)
            elif place_to_assess.place_type.model_class() == ContentType(app_label='companies',
                                                                         model='entity').model_class():
                self.add_entity_to_research_methodology(place_to_assess)
            elif place_to_assess.place_type.model_class() == ContentType(app_label='companies',
                                                                         model='department').model_class():
                self.add_department_to_research_methodology(place_to_assess)


class EvaluationReassignCompanyElement:
    def __init__(self, evaluation, CompanyElement, db_alias):
        self.evaluation = evaluation
        self.reassign()
        self.objects = CompanyElement.objects.using(db_alias)

    def set_section(self, section_id):
        company_element = self.objects.get(additional_info__old_section_id=section_id)
        self.evaluation.company_element = company_element
        self.evaluation.save()

    def set_entity(self, entity_id):
        company_element = self.objects.get(additional_info__old_entity_id=entity_id)
        self.evaluation.company_element = company_element
        self.evaluation.save()

    def reassign(self):
        with connection.cursor() as cursor:
            cursor.execute("select section_id, entity_id from projects_evaluation where id = %s", [self.evaluation.pk])
            row = cursor.fetchone()

        if row[0] is not None:
            self.set_section(row[0])
        elif row[1] is not None:
            self.set_entity(row[1])


def migrate_research_methodologies(ResearchMethodology, CompanyElement, db_alias):
    research_methodologies = ResearchMethodology.objects.using(db_alias).all()
    for research_methodology in research_methodologies:
        ResearchMethodologyReassign(research_methodology, CompanyElement, db_alias)


def migrate_evaluations(Evaluation, CompanyElement, db_alias):
    evaluations = Evaluation.objects.using(db_alias).all()
    for evaluation in evaluations:
        EvaluationReassignCompanyElement(evaluation, CompanyElement, db_alias)


def migrate_all(apps, schema_editor):
    CompanyElement = apps.get_model('companies', 'CompanyElement')
    ResearchMethodology = apps.get_model('projects', 'ResearchMethodology')
    Evaluation = apps.get_model('projects', 'Evaluation')
    db_alias = schema_editor.connection.alias

    migrate_research_methodologies(ResearchMethodology, CompanyElement, db_alias)
    migrate_evaluations(Evaluation, CompanyElement, db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0007_auto_20161230_1529'),
    ]

    operations = [
        migrations.RunPython(migrate_all)
    ]
