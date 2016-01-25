from rest_framework import serializers

from mystery_shopping.tenants.models import Tenant
from .models import Industry, Company, Department, Entity, Section

from mystery_shopping.users.serializers import ClientManagerSerializer


class IndustrySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Industry
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    """

    """
    # id = serializers.IntegerField(label='ID', read_only=False)
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.all(), required=False)

    # todo: remove redefinitions, add extra_args

    class Meta:
        model = Section
        fields = '__all__'

    def create(self, validated_data):
        return Section.objects.create(**validated_data)


class EntitySerializer(serializers.ModelSerializer):
    """

    """
    sections = SectionSerializer(many=True)
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.all(), required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False)

    # todo: remove redefinitions, add extra_args

    class Meta:
        model = Entity
        fields = '__all__'

    def create(self, validated_data):
        sections = validated_data.pop('sections', None)

        entity = Entity.objects.create(**validated_data)

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


class DepartmentSerializer(serializers.ModelSerializer):
    """

    """
    manager = ClientManagerSerializer(read_only=True, many=True)
    entities = EntitySerializer(many=True)

    class Meta:
        model = Department
        fields = '__all__'

    def create(self, validated_data):
        entities = validated_data.pop('entities', None)

        department = Department.objects.create(**validated_data)

        for entity in entities:
            entity['department'] = department.id
            entity['tenant'] = department.tenant.id
            entity['city'] = entity['city'].id
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


class CompanySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Company
        fields = '__all__'
