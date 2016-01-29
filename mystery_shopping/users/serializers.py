from rest_framework import serializers

from .models import User
from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant
from .models import ClientProjectManager
from .models import ClientManager
from .models import ClientEmployee
from .models import ProjectWorker
from .models import PersonToAssess
from .models import Shopper
from mystery_shopping.tenants.serializers import TenantSerializer
# from mystery_shopping.companies.serializer_fields import PlaceRelatedField
# from mystery_shopping.users.serializer_fields import ProjectWorkerRelatedField
# from mystery_shopping.projects.serializers import ProjectSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer class for User model
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'confirm_password')

    def create(self, validated_data):
        password = validated_data.get('password', None)
        confirm_password = validated_data.pop('confirm_password', None)

        user = User(**validated_data)

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

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class TenantProductManagerSerializer(serializers.ModelSerializer):
    """Serializer class for TenantProductManager user model.
    """
    user = UserSerializer()
    tenant = TenantSerializer()
    type = serializers.CharField(source='get_type', read_only=True)

    class Meta:
        model = TenantProductManager
        fields = '__all__'


class TenantProjectManagerSerializer(serializers.ModelSerializer):
    """Serializer class for TenantProjectManager user model.
    """
    user = UserSerializer()
    tenant = TenantSerializer()
    type = serializers.CharField(source='get_type', read_only=True)

    class Meta:
        model = TenantProjectManager
        fields = '__all__'


class TenantConsultantSerializer(serializers.ModelSerializer):
    """Serializer class for TenantConsultant user model.
    """
    user = UserSerializer()
    tenant = TenantSerializer()
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



class ClientManagerSerializer(serializers.ModelSerializer):
    """Serializer class for ClientManager user model.
    """
    user = UserSerializer(required=False, allow_null=True)
    # place_repr = PlaceRelatedField(source='place', read_only=True)

    class Meta:
        model = ClientManager
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user', None)
        if user is not None:
            user_ser = UserSerializer(data=user)
            user_ser.is_valid(raise_exception=True)
            user_ser.save()
            user = user_ser.instance

        client_manager = ClientManager.objects.create(user=user, **validated_data)

        return client_manager

    # def update(self, instance, validated_data):
    #     user = validated_data.pop('user', None)
    #     user_instance = User.objects.filter(pk=user.id).first()
    #     user_ser = UserSerializer(instance=user_instance, data=user)
    #     user_ser.is_valid(raise_exception=True)
    #     user_ser.save()
    #
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #
    #     return instance


class ClientEmployeeSerializer(serializers.ModelSerializer):
    """Serializer class for ClientEmployee user model.
    """
    user = UserSerializer(required=False, allow_null=True)

    class Meta:
        model = ClientEmployee
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user', None)

        if user is not None:
            user_ser = UserSerializer(data=user)
            user_ser.is_valid(raise_exception=True)
            user_ser.save()
            user = user_ser.instance

        client_employee = ClientEmployee.objects.create(user=user, **validated_data)

        return client_employee


class ShopperSerializer(serializers.ModelSerializer):
    """Serializer class for Shopper user model.
    """
    class Meta:
        model = Shopper
        fields = '__all__'


class ProjectWorkerRelatedField(serializers.RelatedField):
    """
    A custom field to use to serialize the instance of a project worker according to it's type: TenantProductManager, TenantProjectManager or TenantConsultant.
    """

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if isinstance(value, TenantProductManager):
            serializer = TenantProductManagerSerializer(value)
        elif isinstance(value, TenantProjectManager):
            serializer = TenantProjectManagerSerializer(value)
        elif isinstance(value, TenantConsultant):
            serializer = TenantConsultantSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data



class ProjectWorkerSerializer(serializers.ModelSerializer):
    """Serializer class for ProjectWorker.
    """
    project_worker_repr = ProjectWorkerRelatedField(source='project_worker', read_only=True)

    class Meta:
        model = ProjectWorker
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
