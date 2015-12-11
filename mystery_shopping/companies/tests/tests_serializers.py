import json

from django.test import TestCase
from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase
from . import factories
from ..models import Department, Entity, Section
from ..serializers import DepartmentSerializer, EntitySerializer, SectionSerializer


json_data = json.load(open("mystery_shopping/companies/tests/Departments.json"))
first = json_data[0]


class DepartmentAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'department'
    factory_class = factories.DepartmentFactory
    update_data = {'name': "Grigory Leps"}

    def get_create_data(self):
        self.data = first['data']
        self.data.pop('entities', None)
        self.data['company'] = self.object.company.pk
        self.data['tenant'] = self.object.tenant.pk
        return self.data


json_data = json.load(open("mystery_shopping/companies/tests/Entities.json"))
first = json_data[0]


class EntityAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'entity'
    factory_class = factories.EntityFactory
    update_data = {'name': "Entity of Leps"}

    def get_create_data(self):
        self.data = first['data']
        self.data.pop('sections', None)
        self.data['department'] = self.object.department.pk
        self.data['city'] = self.object.city.pk
        self.data['sector'] = self.object.sector.pk
        self.data['tenant'] = self.object.tenant.pk
        return self.data


json_data = json.load(open("mystery_shopping/companies/tests/Sectors.json"))
first = json_data[0]


class SectionAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'section'
    factory_class = factories.SectionFactory
    update_data = {'name': "Section of Leps"}

    def get_create_data(self):
        self.data = first['data']
        self.data['entity'] = self.object.entity.pk
        self.data['tenant'] = self.object.tenant.pk
        return self.data
