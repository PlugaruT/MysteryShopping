from rest_framework import serializers


from .models import Department
from .models import Entity
from .models import Section
#
# from .serializers import DepartmentSerializer
# from .serializers import EntitySerializer
# from .serializers import SectionSerializer


class PlaceRelatedField(serializers.RelatedField):
    """

    """
    def to_representation(self, value):
        if isinstance(value, Department):
            return "Department: " + value.name
            # serializer = DepartmentSerializer(value)
        elif isinstance(value, Entity):
            return "Entity: " + value.name
            # serializer = EntitySerializer(value)
        elif isinstance(value, Section):
            return "Section: " + value.name
            # serializer = SectionSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')
