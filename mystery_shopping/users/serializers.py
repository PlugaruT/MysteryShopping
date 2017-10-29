import re

from django.contrib.auth.models import Permission, Group
from guardian.shortcuts import assign_perm, remove_perm
from rest_framework import serializers

from mystery_shopping.companies.serializers import SimpleCompanyElementSerializer
from mystery_shopping.users.models import ClientUser
from .models import User
from .models import PersonToAssess
from .models import Shopper
from .models import Collector

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.tenants.serializers import TenantSerializer


class AssignCustomObjectPermissions:
    """
    Mixin class for assigning custom permissions to user for viewing detractors, statistics
    and coded causes for different company elements
    """

    def assign_object_permissions(self, user_instance, object_permissions):
        companies_for_detractors = object_permissions.get('detractor_permissions', [])
        companies_for_statistics = object_permissions.get('statistics_permissions', [])
        companies_for_coded_causes = object_permissions.get('coded_causes_permissions', [])
        companies_for_management = object_permissions.get('manager_permissions', [])
        self.clear_all_permissions(user_instance)
        self.assign_detractors_permissions(user_instance, companies_for_detractors)
        self.assign_statistics_permissions(user_instance, companies_for_statistics)
        self.assign_coded_cause_permissions(user_instance, companies_for_coded_causes)
        self.assign_manager_permissions(user_instance, companies_for_management)

    def assign_detractors_permissions(self, user_instance, company_elements):
        to_add_company_elements_detractors = self.filter_company_elements(company_elements)
        assign_perm('view_detractors_for_companyelement', user_instance, to_add_company_elements_detractors)

    def assign_statistics_permissions(self, user_instance, company_elements):
        to_add_company_elements_statistics = self.filter_company_elements(company_elements)
        assign_perm('view_statistics_for_companyelement', user_instance, to_add_company_elements_statistics)

    def assign_coded_cause_permissions(self, user_instance, company_elements):
        to_add_company_elements_coded_causes = self.filter_company_elements(company_elements)
        assign_perm('view_coded_causes_for_companyelement', user_instance, to_add_company_elements_coded_causes)

    def assign_manager_permissions(self, user_instance, company_elements):
        to_add_company_elements_manager = self.filter_company_elements(company_elements)
        assign_perm('manager_companyelement', user_instance, to_add_company_elements_manager)

    @staticmethod
    def filter_company_elements(company_elements_ids):
        return CompanyElement.objects.filter(id__in=company_elements_ids)

    def clear_all_permissions(self, user_instance):
        to_remove_company_elements_manager = self.filter_company_elements(user_instance.management_permissions())
        to_remove_company_elements_coded_causes = self.filter_company_elements(user_instance.coded_causes_permissions())
        to_remove_company_elements_statistics = self.filter_company_elements(user_instance.statistics_permissions())
        to_remove_company_elements_detractors = self.filter_company_elements(user_instance.detractors_permissions())
        remove_perm('view_detractors_for_companyelement', user_instance, to_remove_company_elements_detractors)
        remove_perm('view_statistics_for_companyelement', user_instance, to_remove_company_elements_statistics)
        remove_perm('view_coded_causes_for_companyelement', user_instance, to_remove_company_elements_coded_causes)
        remove_perm('manager_companyelement', user_instance, to_remove_company_elements_manager)

    @staticmethod
    def create_or_update_user(data, user_instance=None):
        data['tenant'] = data['tenant'].id
        user_ser = UserSerializer(user_instance, data=data)
        user_ser.is_valid(raise_exception=True)
        user_ser.save()
        return user_ser.instance


class UsersCreateMixin(AssignCustomObjectPermissions):
    """
    Mixin class used to create (almost) all types of users.
    """

    def create(self, validated_data):
        user = validated_data.pop('user', None)
        groups = user.pop('groups', [])
        user_permissions = user.pop('user_permissions', [])
        object_permissions = validated_data.pop('object_permissions', None)
        if user:
            user_instance = self.create_or_update_user(user)
            user_instance.groups.add(*groups)
            user_instance.user_permissions.add(*user_permissions)
            if object_permissions:
                self.assign_object_permissions(user_instance, object_permissions)

        user_type = self.Meta.model.objects.create(user=user_instance, **validated_data)

        return user_type


class UsersUpdateMixin(AssignCustomObjectPermissions):
    """
    Mixin class used to update (almost) all types of users.
    """

    def update(self, instance, validated_data):
        user = validated_data.pop('user', None)
        groups = user.pop('groups', [])
        user_permissions = user.pop('user_permissions', [])
        object_permissions = validated_data.pop('object_permissions', None)
        if user:
            if user.get('username', None) != instance.user.username:
                user['change_username'] = True
            user_ser = self.create_or_update_user(user, instance.user)
            user_ser.groups.clear()
            user_ser.groups.add(*groups)
            user_ser.user_permissions.add(*user_permissions)
            if object_permissions:
                self.assign_object_permissions(user_ser, object_permissions)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer class for Permission model
    """

    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer class for Group model
    """

    permissions = PermissionSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(AssignCustomObjectPermissions, serializers.ModelSerializer):
    """
    Serializer class for User model
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    change_username = serializers.BooleanField(write_only=True, required=False)
    object_permissions = serializers.JSONField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'change_username',
                  'password', 'confirm_password', 'tenant', 'user_permissions', 'groups',
                  'date_of_birth', 'gender', 'object_permissions', 'phone_number')
        extra_kwargs = {
            'username': {
                'validators': []
            },
            'tenant': {
                'required': False
            },
            'shopper': {
                'read_only': True
            },
            'company': {
                'read_only': True
            },
            'help_text': 'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'
        }

    def create(self, validated_data):
        password = validated_data.get('password', None)
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])
        object_permissions = validated_data.pop('object_permissions', None)
        confirm_password = validated_data.pop('confirm_password', None)
        validated_data.pop('change_username', None)
        self.check_username(validated_data['username'])
        user = User(**validated_data)
        self.check_username(validated_data['username'])

        if password and confirm_password and password == confirm_password:
            user.set_password(password)
        else:
            raise serializers.ValidationError({'password': ['Provided passwords do not match.']})

        user.save()
        user.groups.add(*groups)
        user.user_permissions.add(*user_permissions)
        if object_permissions:
            self.assign_object_permissions(user, object_permissions)
        return user

    def update(self, instance, validated_data):
        # TODO improve password validation on update
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])
        object_permissions = validated_data.pop('object_permissions', None)
        confirm_password = validated_data.pop('confirm_password', None)

        if password and confirm_password:
            if password == confirm_password:
                instance.set_password(password)
                instance.save()
                # TODO change update_session_auth_hash to JWT_token_update
                # update_session_auth_hash(self.context.get('request'), instance)
            else:
                raise serializers.ValidationError({'password': ['Provided passwords do not match.']})

        if validated_data.get('change_username', False) and (validated_data.get('username', None) != instance.username):
            username = validated_data.get('username', None)
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError({
                    'username': ['Username: \'{}\' is already taken, please choose another one.'.format(username)]})
            self.check_username(username)
        else:
            validated_data.pop('username', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.groups.clear()
        instance.groups.add(*groups)
        instance.user_permissions.add(*user_permissions)
        if object_permissions:
            self.assign_object_permissions(instance, object_permissions)
        return instance

    @staticmethod
    def check_username(username):
        # Todo: add regex checking for 'username' characters
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'key': 'VALIDATION_MESSAGE.USER.USERNAME_EXISTS'
            })
        if not re.match("^[a-zA-Z0-9@.+-_]+$", username):
            raise serializers.ValidationError({
                'key': 'VALIDATION_MESSAGE.USER.ILLEGAL_CHARS'
            })
        # No need to check len(username) > 30, as it does it by itself.
        return True


class UserSerializerGET(UserSerializer):
    """
    Serializer class that is used only for GET method
    """
    user_permissions = PermissionSerializer(many=True, read_only=False)
    groups = GroupSerializer(many=True, read_only=False)
    roles = serializers.ListField(read_only=True, source='user_roles')
    tenant = TenantSerializer(read_only=True)
    object_permissions = serializers.JSONField(source='get_company_elements_permissions', read_only=True)
    company = SimpleCompanyElementSerializer(source='user_company', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'change_username',
                  'password', 'confirm_password', 'tenant', 'user_permissions', 'groups',
                  'date_of_birth', 'gender', 'roles', 'object_permissions', 'phone_number', 'company')


class ShopperSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """
    Serializer class for Shopper user model.
    """
    user = UserSerializer()

    class Meta:
        model = Shopper
        fields = '__all__'


class ShopperSerializerGET(serializers.ModelSerializer):
    """
    Serializer class for Shopper user model.
    """
    user = UserSerializerGET()

    class Meta:
        model = Shopper
        fields = '__all__'


class ClientUserSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """
    Serializer class for client users
    """
    user = UserSerializer()

    class Meta:
        model = ClientUser
        fields = '__all__'


class ClientUserSerializerGET(serializers.ModelSerializer):
    """
    Serializer class for client users
    """
    user = UserSerializerGET()

    class Meta:
        model = ClientUser
        fields = '__all__'


class CollectorSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for Shopper user model.
    """
    user = UserSerializer()

    class Meta:
        model = Collector
        fields = '__all__'


class PersonToAssessSerializer(serializers.ModelSerializer):
    """

    """

    class Meta:
        model = PersonToAssess
        fields = '__all__'
        extra_kwargs = {'research_methodology': {'required': False}}
