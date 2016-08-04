from rest_framework import serializers

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
    country_repr = CountrySerializer(source='country', read_only=True)

    class Meta:
        model = Company
        fields = '__all__'
