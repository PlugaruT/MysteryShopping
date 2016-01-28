from rest_framework import serializers

from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant
from .models import ClientManager
from .models import ClientEmployee

# from mystery_shopping.projects.serializers import ProjectSerializer
from .serializers import TenantProductManagerSerializer
from .serializers import TenantProjectManagerSerializer
from .serializers import TenantConsultantSerializer
from .serializers import ClientManagerSerializer
from .serializers import ClientEmployeeSerializer


class ProjectManagerRelatedField(serializers.RelatedField):
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
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class ClientUserRelatedField(serializers.RelatedField):
    """
    A custom field to use to serialize the instance (from a Planned and Accomplished evaluations) of a client employee according to it's type: ClientManager or ClientEmployee.
    """

    def to_representation(self, value):
        """
        Serialize a project_manager instance according to it's type.
        """
        if isinstance(value, ClientManager):
            serializer = ClientManagerSerializer(value)
        elif isinstance(value, ClientEmployee):
            serializer = ClientEmployeeSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


    #
    # def to_internal_value(self, data):
    #     pass
