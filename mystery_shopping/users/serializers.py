import re

from rest_framework import serializers

from .models import User
from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant
from .models import ClientProjectManager
from .models import ClientManager
from .models import ClientEmployee
from .models import PersonToAssess
from .models import Shopper
from .models import Collector

from mystery_shopping.companies.models import Company
from mystery_shopping.tenants.serializers import TenantSerializer


class SimpleCompanySerializer(serializers.ModelSerializer):
    """A Company serializer that does not have any nested serializer fields."""

    class Meta:
        model = Company
        fields = '__all__'


class UsersCreateMixin:
    '''
    Mixin class used to create (almost) all types of users.

    '''
    def create(self, validated_data):
        user = validated_data.pop('user', None)

        if user:
            user_ser = UserSerializer(data=user)
            user_ser.is_valid(raise_exception=True)
            user_ser.save()
            user = user_ser.instance

        user_type = self.Meta.model.objects.create(user=user, **validated_data)

        return user_type


class UsersUpdateMixin:
    '''
    Mixin class used to update (almost) all types of users.

    '''
    def update(self, instance, validated_data):
        user = validated_data.pop('user', None)

        if user:
            if user.get('username', None) != instance.user.username:
                user['change_username'] = True
            user_ser = UserSerializer(instance.user, data=user)
            user_ser.is_valid(raise_exception=True)
            user_ser.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    """Serializer class for User model
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    tenant_repr = TenantSerializer(source='tenant', read_only=True)
    roles = serializers.ListField(read_only=True, source='user_roles')
    change_username = serializers.BooleanField(write_only=True, required=False)
    company = SimpleCompanySerializer(source='user_company', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'change_username',
                  'roles', 'password', 'confirm_password', 'tenant_repr', 'shopper', 'company')
        extra_kwargs = {'username': {'validators': []},
                        'shopper': {'read_only': True},
                        'company': {'read_only': True},
                        'help_text': 'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'}

    @staticmethod
    def check_username(username):
        # Todo: add regex checking for 'username' characters
        if User.objects.filter(username=username).count():
            raise serializers.ValidationError({
                'username': ['Username: \'{}\' is already taken, please choose another one.'.format(username)]
            })
        if not re.match("^[a-zA-Z0-9@.+-_]+$", username):
            raise serializers.ValidationError({
                'username': ['Username: \'{}\' contains illegal characters.'
                             ' Allowed characters: letters, digits and @/./+/-/_ only.'.format(username)]
            })
        # No need to check len(username) > 30, as it does it by itself.
        return True

    def create(self, validated_data):
        password = validated_data.get('password', None)
        confirm_password = validated_data.pop('confirm_password', None)

        user = User(**validated_data)
        self.check_username(validated_data['username'])

        if password and confirm_password and password == confirm_password:
            user.set_password(password)
        else:
            raise serializers.ValidationError({'password': ['Provided passwords do not match.']})

        user.save()
        return user

    def update(self, instance, validated_data):
        # TODO improve password validation on update
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)

        if password and confirm_password:
            if password == confirm_password:
                instance.set_password(password)
                instance.save()
                # TODO change update_session_auth_hash to JWT_token_update
                # update_session_auth_hash(self.context.get('request'), instance)
            else:
                raise serializers.ValidationError({'password': ['Provided passwords do not match.']})

        if validated_data.get('change_username', False):
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

        return instance


class TenantProductManagerSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for TenantProductManager user model.
    """
    user = UserSerializer()
    tenant_repr = TenantSerializer(source='tenant', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)

    class Meta:
        model = TenantProductManager
        fields = '__all__'


class TenantProjectManagerSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for TenantProjectManager user model.
    """
    user = UserSerializer()
    tenant_repr = TenantSerializer(source='tenant', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)

    class Meta:
        model = TenantProjectManager
        fields = '__all__'


class TenantConsultantSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for TenantConsultant user model.
    """
    user = UserSerializer()
    tenant_repr = TenantSerializer(source='tenant', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)

    class Meta:
        model = TenantConsultant
        fields = '__all__'


class ClientProjectManagerSerializer(serializers.ModelSerializer):
    """Serializer class for ClientProjectManager user model.
    """
    class Meta:
        model = ClientProjectManager
        fields = '__all__'


class ClientManagerSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for ClientManager user model.
    """
    user = UserSerializer(required=False, allow_null=True)

    class Meta:
        model = ClientManager
        fields = '__all__'


class ClientEmployeeSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for ClientEmployee user model.
    """
    user = UserSerializer(required=False, allow_null=True)
    company_repr = SimpleCompanySerializer(source='company', read_only=True)

    class Meta:
        model = ClientEmployee
        fields = '__all__'


class ShopperSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for Shopper user model.
    """
    user = UserSerializer()

    class Meta:
        model = Shopper
        fields = '__all__'

class CollectorSerializer(UsersCreateMixin, UsersUpdateMixin, serializers.ModelSerializer):
    """Serializer class for Shopper user model.
    """
    user = UserSerializer()

    class Meta:
        model = Collector
        fields = '__all__'


class PersonToAssessRelatedField(serializers.RelatedField):
    """
    A custom field to use to serialize the instance of a person to assess according to it's type: ClientManager or ClientEmployee.
    """
    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if isinstance(value, ClientManager):
            serializer = ClientManagerSerializer(value)
        elif isinstance(value, ClientEmployee):
            serializer = ClientEmployeeSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class PersonToAssessSerializer(serializers.ModelSerializer):
    """

    """
    person_repr = PersonToAssessRelatedField(source='person', read_only=True)

    class Meta:
        model = PersonToAssess
        fields = '__all__'
        extra_kwargs = {'research_methodology': {'required': False}}

