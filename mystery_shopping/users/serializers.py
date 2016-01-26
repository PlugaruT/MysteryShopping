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
from mystery_shopping.companies.serializer_fields import PlaceRelatedField


class UserSerializer(serializers.ModelSerializer):
    """Serializer class for User model
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


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
    manager_repr = UserSerializer(source='user', read_only=True)
    # place_repr = PlaceRelatedField(source='place', read_only=True)
    class Meta:
        model = ClientManager
        fields = '__all__'


class ClientEmployeeSerializer(serializers.ModelSerializer):
    """Serializer class for ClientEmployee user model.
    """
    employee_repr = UserSerializer(source='user', read_only=True)

    class Meta:
        model = ClientEmployee
        fields = '__all__'


class ShopperSerializer(serializers.ModelSerializer):
    """Serializer class for Shopper user model.
    """
    class Meta:
        model = Shopper
        fields = '__all__'


class ProjectWorkerSerializer(serializers.ModelSerializer):
    """Serializer class for ProjectWorker.
    """

    class Meta:
        model = ProjectWorker
        fields = '__all__'

    def to_representation(self, instance):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if instance.project_worker_type.model == 'tenantproductmanager':
            to_serialize = TenantProductManager.objects.get(pk=instance.project_worker_id)
            serializer = TenantProductManagerSerializer(to_serialize)
        elif instance.project_worker_type.model == 'tenantprojectmanager':
            to_serialize = TenantProjectManager.objects.get(pk=instance.project_worker_id)
            serializer = TenantProjectManagerSerializer(to_serialize)
        elif instance.project_worker_type.model == 'tenantconsultant':
            to_serialize = TenantConsultant.objects.get(pk=instance.project_worker_id)
            serializer = TenantConsultantSerializer(to_serialize)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data

#     todo: define to_representation as a related field


class PersonToAssessSerializer(serializers.ModelSerializer):
    """

    """

    class Meta:
        model = PersonToAssess
        fields = '__all__'

    def to_representation(self, instance):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if instance.project_worker_type.model == 'clientmanager':
            to_serialize = ClientManager.objects.get(pk=instance.project_worker_id)
            serializer = ClientManager(to_serialize)
        elif instance.project_worker_type.model == 'clientemployee':
            to_serialize = ClientEmployee.objects.get(pk=instance.project_worker_id)
            serializer = ClientEmployeeSerializer(to_serialize)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data
