# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.cxi.models import ProjectComment


def set_section_comment(project_comment):
    company_element = CompanyElement.objects.get(additional_info__old_section_id=project_comment.section.pk)
    project_comment.company_element = company_element
    project_comment.save()


def set_entity_comment(project_comment):
    company_element = CompanyElement.objects.get(additional_info__old_entity_id=project_comment.entity.pk)
    project_comment.company_element = company_element
    project_comment.save()



def set_department_comment(project_comment):
    company_element = CompanyElement.objects.get(additional_info__old_department_id=project_comment.department.pk)
    project_comment.company_element = company_element
    project_comment.save()


def migrate_comments(*args):
    project_comments = ProjectComment.objects.all()
    for project_comment in project_comments:
        if project_comment.section is not None:
            set_section_comment(project_comment)
        elif project_comment.entity is not None:
            set_entity_comment(project_comment)
        elif project_comment.department is not None:
            set_department_comment(project_comment)


class Migration(migrations.Migration):
    dependencies = [

        ('companies', '0007_companyelement'),
        ('cxi', '0008_auto_20161018_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectcomment',
            name='company_element',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_comments', to='companies.CompanyElement'),
        ),
        migrations.RunPython(migrate_comments)
    ]
