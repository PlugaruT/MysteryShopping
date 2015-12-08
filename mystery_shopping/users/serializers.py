from rest_framework import serializers

from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant
from .models import ClientProjectManager
from .models import ClientManager
from .models import ClientEmployee


class TenantProductManagerSerializer(serializers.ModelSerializer):
    """Serializer class for TenantProductManager user model.
    """
    class Meta:
        model = TenantProductManager
        fields = '__all__'


class TenantProjectManagerSerializer(serializers.ModelSerializer):
    """Serializer class for TenantProjectManager user model.
    """
    class Meta:
        model = TenantProjectManager
        fields = '__all__'


class TenantConsultantSerializer(serializers.ModelSerializer):
    """Serializer class for TenantConsultant user model.
    """
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