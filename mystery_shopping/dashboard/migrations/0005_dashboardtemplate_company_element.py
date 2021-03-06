# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.dashboard.models import DashboardTemplate


class DashboardReassignCompany:
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.reassign()

    def reassign(self):
        company_element = CompanyElement.objects.get(additional_info__old_company_id=self.dashboard.company.id)
        self.dashboard.company_element = company_element
        self.dashboard.save()


def migrate_dashboards(*args):
    dashboards = DashboardTemplate.objects.all()
    for dashboard in dashboards:
        DashboardReassignCompany(dashboard)


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0007_companyelement'),
        ('dashboard', '0004_auto_20160826_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardtemplate',
            name='company_element',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='companies.CompanyElement'),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_dashboards)
    ]
