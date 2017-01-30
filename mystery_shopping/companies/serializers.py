from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from mystery_shopping.companies.models import SubIndustry, CompanyElement, AdditionalInfoType
from .models import Industry, Company, Department, Entity, Section

from mystery_shopping.common.serializer import CitySerializer
from mystery_shopping.common.serializer import CountrySerializer
from mystery_shopping.users.serializers import ClientManagerSerializer
from mystery_shopping.users.serializers import ClientEmployeeSerializer


class IndustrySerializer(serializers.ModelSerializer):
    """

    """

    class Meta:
        model = Industry
        fields = '__all__'


class SubIndustrySerializer(serializers.ModelSerializer):
    """

    """
    full_name = serializers.CharField(source='return_industry_and_subindustry', read_only=True)
    industry = IndustrySerializer(read_only=True)

    class Meta:
        model = SubIndustry
        fields = '__all__'


class RecursiveFieldSerializer(serializers.BaseSerializer):
    """
    Serializer class used for recursive serialization of parent field from CompanyElement model
    """

    def to_representation(self, value):
        ParentSerializer = self.parent.parent.__class__
        serializer = ParentSerializer(value, context=self.context)
        return serializer.data

    def to_internal_value(self, data):
        ParentSerializer = self.parent.parent.__class__
        Model = ParentSerializer.Meta.model
        try:
            instance = Model.objects.get(pk=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Object {0} not found".format(
                    Model().__class__.__name__
                )
            )
        return instance


class CompanyElementSerializer(serializers.ModelSerializer):
    """
    Serializer class used for serializing CompanyElement model
    """
    children = RecursiveFieldSerializer(many=True, required=False, read_only=True)
    additional_info = serializers.JSONField(required=False)

    class Meta:
        model = CompanyElement
        fields = ('id', 'element_name', 'element_type', 'children', 'additional_info', 'parent', 'tenant', 'order')
        extra_kwargs = {
            'tenant': {
                'required': False
            },
            'additional_info': {
                'allow_blank': True
            }
        }


    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('parent')
        return queryset


class SimpleCompanyElementSerializer(serializers.ModelSerializer):
    """
    Serializer class used for serializing only top level CompanyElement model (companies)
    """
    additional_info = serializers.JSONField(read_only=True)

    class Meta:
        model = CompanyElement
        fields = ('id', 'element_name', 'element_type', 'additional_info', 'tenant')


class AdditionalInfoTypeSerializer(serializers.ModelSerializer):
    """
    Serialize class for AdditionalInfoType model
    """

    class Meta:
        model = AdditionalInfoType
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    """

    """
    managers = ClientManagerSerializer(read_only=True, many=True)
    employees = ClientEmployeeSerializer(read_only=True, many=True)

    # todo: remove redefinitions, add extra_args

    class Meta:
        model = Section
        fields = '__all__'
        extra_kwargs = {'entity': {'required': False}}

    def create(self, validated_data):
        return Section.objects.create(**validated_data)


class SimpleSectionSerializer(serializers.ModelSerializer):
    """
        Simple Section representation
    """
    place_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Section
        fields = ('name', 'place_id')


class EntitySerializer(serializers.ModelSerializer):
    """

    """
    city_repr = CitySerializer(source='city', read_only=True)
    managers = ClientManagerSerializer(read_only=True, many=True)
    employees = ClientEmployeeSerializer(read_only=True, many=True)
    sections = SectionSerializer(many=True, required=False)

    # todo: remove redefinitions, add extra_args

    class Meta:
        model = Entity
        fields = '__all__'
        extra_kwargs = {'department': {'required': False}}

    def create(self, validated_data):
        sections = validated_data.pop('sections', None)

        entity = Entity.objects.create(**validated_data)

        if sections is not None:
            for section in sections:
                section['entity'] = entity.id
                section['tenant'] = entity.tenant.id
                section['city'] = section['city'].id
                section_ser = SectionSerializer(data=section)
                section_ser.is_valid(raise_exception=True)
                section_ser.save()
        return entity

    def update(self, instance, validated_data):
        validated_data.pop('sections')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class SimpleEntitySerializer(serializers.ModelSerializer):
    """
    Simple Entity representation
    """
    place_id = serializers.IntegerField(source='id', read_only=True)
    sections = SimpleSectionSerializer(many=True)

    class Meta:
        model = Entity
        fields = ('name', 'place_id', 'sections')


class DepartmentSerializer(serializers.ModelSerializer):
    """

    """
    managers = ClientManagerSerializer(read_only=True, many=True)
    entities = EntitySerializer(many=True, required=False)

    class Meta:
        model = Department
        fields = '__all__'

    def create(self, validated_data):
        entities = validated_data.pop('entities', None)

        department = Department.objects.create(**validated_data)

        if entities is not None:
            for entity in entities:
                entity['department'] = department.id
                entity['tenant'] = department.tenant.id
                entity['city'] = entity['city'].id
                # TODO change this piece of code. This is not sexy at all.
                try:
                    entity['sector'] = entity['sector'].id
                except:
                    pass
                entity_ser = EntitySerializer(data=entity)
                entity_ser.is_valid(raise_exception=True)
                entity_ser.save()
        return department

    def update(self, instance, validated_data):
        validated_data.pop('entities', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class SimpleDepartmentSerializer(serializers.ModelSerializer):
    """
    Simple representation of a department
    """
    place_id = serializers.IntegerField(source='id', read_only=True)
    entities = SimpleEntitySerializer(many=True)

    class Meta:
        model = Department
        fields = ('place_id', 'entities')


class CompanySerializer(serializers.ModelSerializer):
    """

    """
    departments_repr = DepartmentSerializer(source='departments', many=True, read_only=True)
    industry_repr = IndustrySerializer(source='industry', read_only=True)
    subindustry_repr = SubIndustrySerializer(source='subindustry', read_only=True)
    country_repr = CountrySerializer(source='country', read_only=True)

    class Meta:
        model = Company
        fields = '__all__'
