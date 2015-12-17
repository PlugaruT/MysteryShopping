from rest_framework import serializers

from .models import User
from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant
from .models import ClientProjectManager
from .models import ClientManager
from .models import ClientEmployee
from .models import ProjectWorker
from .models import Shopper
from mystery_shopping.tenants.serializers import TenantSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer class for User model
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class TenantProductManagerSerializer(serializers.ModelSerializer):
    """Serializer class for TenantProductManager user model.
    """
    class Meta:
        model = TenantProductManager
        fields = '__all__'


class TenantProjectManagerSerializer(serializers.ModelSerializer):
    """Serializer class for TenantProjectManager user model.
    """
    user = UserSerializer()
    tenant = TenantSerializer()

    class Meta:
        model = TenantProjectManager
        fields = '__all__'


class TenantConsultantSerializer(serializers.ModelSerializer):
    """Serializer class for TenantConsultant user model.
    """
    user = UserSerializer()
    tenant = TenantSerializer()

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
    class Meta:
        model = ClientManager
        fields = '__all__'


class ClientEmployeeSerializer(serializers.ModelSerializer):
    """Serializer class for ClientEmployee user model.
    """
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
        print(instance.object_id)
        print(instance.content_type.model)
        if instance.content_type.model == 'tenantprojectmanager':
            to_serialize = TenantProjectManager.objects.get(pk=instance.object_id)
            serializer = TenantProjectManagerSerializer(to_serialize)
        elif instance.content_type.model == 'tenantconsultant':
            to_serialize = TenantConsultant.objects.get(pk=instance.object_id)
            serializer = TenantConsultantSerializer(to_serialize)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


