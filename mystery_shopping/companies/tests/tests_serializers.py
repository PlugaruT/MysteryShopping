import json

from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.companies import DepartmentFactory, EntityFactory, SectionFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory


# # TODO write .update()
# class DepartmentAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):
#
#     base_name = 'department'
#     factory_class = DepartmentFactory
#     user_factory = UserThatIsTenantProductManagerFactory
#     update_data = {'name': "Grigory Leps"}
#
#     def get_create_data(self):
#         json_data = json.load(open("mystery_shopping/companies/tests/Departments.json"))
#         first = json_data[0]
#         self.data = first['data']
#         print("from department test")
#         print(self.data)
#         self.data.pop('entities', None)
#         self.data['company'] = self.object.company.pk
#         self.data['tenant'] = self.object.tenant.pk
#         return self.data
#
#
# # TODO write .update()
# class EntityAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):
#
#     base_name = 'entity'
#     factory_class = EntityFactory
#     user_factory = UserThatIsTenantProductManagerFactory
#     update_data = {'name': "Entity of Leps"}
#
#     def get_create_data(self):
#         json_data = json.load(open("mystery_shopping/companies/tests/Entities.json"))
#         first = json_data[0]
#         self.data = first['data']
#         print("from entity test")
#         print(self.data)
#         self.data.pop('sections', None)
#         self.data['department'] = self.object.department.pk
#         self.data['city'] = self.object.city.pk
#         self.data['sector'] = self.object.sector.pk
#         self.data['tenant'] = self.object.tenant.pk
#         return self.data
#
#
# class SectionAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):
#
#     base_name = 'section'
#     factory_class = SectionFactory
#     user_factory = UserThatIsTenantProductManagerFactory
#     update_data = {'name': "Section of Leps"}
#
#     def get_create_data(self):
#         json_data = json.load(open("mystery_shopping/companies/tests/Sectors.json"))
#         first = json_data[0]
#         self.data = first['data']
#         self.data['entity'] = self.object.entity.pk
#         self.data['tenant'] = self.object.tenant.pk
#         return self.data
