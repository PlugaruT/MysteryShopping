from rest_framework import serializers

from .models import CodedCauseLabel
from .models import CodedCause


class CodedCauseLabelSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CodedCauseLabel
        fields = '__all__'


class CodedCauseSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CodedCause
        fields = '__all__'