from rest_framework import serializers

from .models import WhyCause
from .models import CodedCauseLabel
from .models import CodedCause
from .models import ProjectComment

from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.questionnaires.utils import update_attributes


class CodedCauseLabelSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CodedCauseLabel
        fields = '__all__'
        extra_kwargs = {'tenant': {'required': False}}


class WhyCauseSerializer(serializers.ModelSerializer):
    """
    Serializer for WhyCause model
    """
    split_list = serializers.ListField(write_only=True, required=False)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('question')
        queryset = queryset.prefetch_related('coded_causes', 'coded_causes__raw_causes')
        return queryset

    class Meta:
        model = WhyCause
        fields = ('id', 'answer', 'is_appreciation_cause', 'coded_causes', 'question', 'split_list')
        extra_kwargs = {
            'question': {
                'required': False
            },
            'coded_causes': {
                'required': False
            }
        }


class SimpleQuestionnaireQuestionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='additional_info', read_only=True)

    class Meta:
        model = QuestionnaireQuestion
        fields = ('type', 'id', 'score')
        read_only_fields = ('type', 'id', 'score')


class SimpleWhyCauseSerializer(serializers.ModelSerializer):
    question = SimpleQuestionnaireQuestionSerializer()

    class Meta:
        model = WhyCause
        fields = ('id', 'answer', 'is_appreciation_cause', 'coded_causes', 'question')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('question')
        queryset = queryset.prefetch_related('coded_causes')
        return queryset


class CodedCauseSerializer(serializers.ModelSerializer):
    """
        Serializer for coded causes
    """
    coded_label = CodedCauseLabelSerializer()
    why_causes = WhyCauseSerializer(source='get_few_why_causes', many=True, read_only=True)
    why_causes_count = serializers.IntegerField(source='get_number_of_why_causes', read_only=True)

    class Meta:
        model = CodedCause
        extra_kwargs = {'tenant': {'required': False}}
        exclude = ('raw_causes',)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('coded_label', 'coded_label__tenant', 'project')
        queryset = queryset.prefetch_related('raw_causes', 'raw_causes__question', 'raw_causes__coded_causes')
        return queryset

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

    def update(self, instance, validated_data):
        self.update_coded_label(instance, validated_data.pop('coded_label'))
        update_attributes(validated_data, instance)
        instance.save()
        return instance

    @staticmethod
    def update_coded_label(instance, coded_label):
        instance.coded_label.name = coded_label['name']
        instance.coded_label.tenant = coded_label['tenant']
        instance.coded_label.save()


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
        extra_kwargs = {
            'indicator': {
                'allow_null': True
            }
        }

    def validate(self, attrs):
        indicator = attrs.get('indicator')
        if indicator is None:
            attrs['indicator'] = ''
        return attrs
