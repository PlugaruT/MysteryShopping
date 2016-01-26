from rest_framework import serializers

from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant

from .serializers import TenantProductManagerSerializer
from .serializers import TenantProjectManagerSerializer
from .serializers import TenantConsultantSerializer


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

#
# class ProjectWorkerRelatedField(serializers.RelatedField):
#     """
#     A custom field to use to serialize the instance of a project worker according to it's type: TenantProductManager, TenantProjectManager or TenantConsultant.
#     """
#
#     def to_representation(self, instance):
#         """
#         Serialize tagged objects to a simple textual representation.
#         """
#         if instance.content_type.model == 'tenantproductmanager':
#             to_serialize = TenantProductManager.objects.get(pk=instance.object_id)
#             serializer = TenantProductManagerSerializer(to_serialize)
#         elif instance.content_type.model == 'tenantprojectmanager':
#             to_serialize = TenantProjectManager.objects.get(pk=instance.object_id)
#             serializer = TenantProjectManagerSerializer(to_serialize)
#         elif instance.content_type.model == 'tenantconsultant':
#             to_serialize = TenantConsultant.objects.get(pk=instance.object_id)
#             serializer = TenantConsultantSerializer(to_serialize)
#         else:
#             raise Exception('Unexpected type of tagged object')
#
#         return serializer.data
