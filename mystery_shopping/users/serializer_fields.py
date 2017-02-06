from rest_framework import serializers

from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant

from .serializers import TenantProductManagerSerializer
from .serializers import TenantProjectManagerSerializer
from .serializers import TenantConsultantSerializer


class TenantUserRelatedField(serializers.RelatedField):
    """
    A custom field to use to serialize the instance (from a Project) of a project manager according to it's type: TenantProductManager or TenantProjectManager.
    """

    def to_representation(self, value):
        """
        Serialize a project_manager instance according to it's type.
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
