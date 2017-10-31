from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from mystery_shopping.companies.models import AdditionalInfoType, CompanyElement, Industry, SubIndustry


class IndustrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = '__all__'


class SubIndustrySerializer(serializers.ModelSerializer):

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
    Serializer class used for serializing CompanyElement model
    """
    additional_info = serializers.JSONField(required=False)

    class Meta:
        model = CompanyElement
        fields = ('id', 'element_name', 'element_type', 'additional_info', 'parent')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('parent')
        return queryset


class AdditionalInfoTypeSerializer(serializers.ModelSerializer):
    """
    Serialize class for AdditionalInfoType model
    """

    class Meta:
        model = AdditionalInfoType
        fields = '__all__'
