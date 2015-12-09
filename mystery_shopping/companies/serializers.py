from rest_framework import serializers

from mystery_shopping.tenants.models import Tenant
from .models import Industry, Company, Department, Entity, Section


class IndustrySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Industry
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    """

    """
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.all(), required=False)

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

    class Meta:
        model = Entity
        fields = '__all__'

    def create(self, validated_data):
        print("inside entity")
        print(validated_data)
        sections = validated_data.pop('sections', None)

        entity = Entity.objects.create(**validated_data)

        for section in sections:
            print(section)
            section['entity'] = entity.id
            section['tenant'] = entity.tenant.id
            print()
            print(section['city'].id)
            print()
            section['city'] = section['city'].id
            section_ser = SectionSerializer(data=section)
            section_ser.is_valid(raise_exception=True)
            section_ser.save()
        return entity


class DepartmentSerializer(serializers.ModelSerializer):
    """

    """
    entities = EntitySerializer(many=True)

    class Meta:
        model = Department
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        entities = validated_data.pop('entities', None)

        department = Department.objects.create(**validated_data)

        for entity in entities:
            print("inside department loop")
            print(entity)
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


class CompanySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Company
        fields = '__all__'
