from rest_framework import serializers

from mystery_shopping.cxi.models import WhyCause
from .models import CodedCauseLabel
from .models import CodedCause
from .models import ProjectComment

from mystery_shopping.questionnaires.models import QuestionnaireQuestion


class CodedCauseLabelSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CodedCauseLabel
        fields = '__all__'
        extra_kwargs = {'tenant' : {'required': False}}


class CodedCauseSerializer(serializers.ModelSerializer):
    """

    """
    coded_label = CodedCauseLabelSerializer()

    class Meta:
        model = CodedCause
        # fields = '__all__'
        exclude = ('raw_causes',)
        extra_kwargs = {'tenant' : {'required': False}}

    def create(self, validated_data):
        coded_cause_label = validated_data.get('coded_label', None)
        coded_cause_label['tenant'] = coded_cause_label['tenant'].pk
        try:
            existent_coded_cause_label = CodedCauseLabel.objects.get(
                name=coded_cause_label.get('name', None),
                tenant=validated_data.get('tenant', None))
            validated_data['coded_label'] = existent_coded_cause_label
        except CodedCauseLabel.DoesNotExist:
            coded_cause_label_ser = CodedCauseLabelSerializer(data=coded_cause_label)
            coded_cause_label_ser.is_valid(raise_exception=True)
            coded_cause_label_ser.save()
            validated_data['coded_label'] = coded_cause_label_ser.instance

        coded_cause = CodedCause.objects.create(**validated_data)

        return coded_cause


class WhyCauseSerializer(serializers.ModelSerializer):
    """
    Serializer for WhyCause model
    """
    answer = serializers.CharField(source='text', read_only=True)

    class Meta:
        model = WhyCause
        fields = ('id', 'answer', 'text', 'is_appreciation_cause', 'coded_causes', 'question')
        extra_kwargs = {
            'question': {
                'write_only': True,
                'required': False
            },
            'coded_causes': {
                'required': False
            }
        }


class QuestionWithWhyCausesSerializer(serializers.ModelSerializer):
    """Serializes only the minimal required fields to be able to encode a question's answer
    for the Customer Experience Index indicators.
    """
    why_causes = WhyCauseSerializer(many=True, read_only=True)
    type = serializers.CharField(source='additional_info', read_only=True)

    class Meta:
        model = QuestionnaireQuestion
        fields = ('type', 'why_causes', 'id', 'score')
        read_only_fields = ('type', 'why_causes', 'id', 'score')


class ProjectCommentSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = ProjectComment
        fields = '__all__'
