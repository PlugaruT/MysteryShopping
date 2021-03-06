from rest_framework import serializers

from mystery_shopping.cxi.models import CodedCause, CodedCauseLabel, ProjectComment, WhyCause
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.questionnaires.utils import update_attributes
from mystery_shopping.users.serializers import SimpleClientUserSerializerGET


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
    responsible_users_repr = SimpleClientUserSerializerGET(many=True, source='responsible_users', read_only=True)

    class Meta:
        model = CodedCause
        exclude = ('raw_causes',)
        extra_kwargs = {
            'tenant': {
                'required': False
            },
        }

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('coded_label', 'coded_label__tenant', 'project')
        queryset = queryset.prefetch_related('raw_causes', 'raw_causes__question', 'raw_causes__coded_causes',
                                             'responsible_users')
        return queryset

    def create(self, validated_data):
        coded_label_data = validated_data.get('coded_label', None)
        responsible_users_data = validated_data.pop('responsible_users', [])

        coded_cause_label = self.create_coded_cause_label(coded_label_data)
        validated_data['coded_label'] = coded_cause_label
        coded_cause = CodedCause.objects.create(**validated_data)

        coded_cause.responsible_users.add(*responsible_users_data)
        return coded_cause

    def update(self, instance, validated_data):
        responsible_users_data = validated_data.pop('responsible_users', None)

        self.update_coded_label(instance, validated_data.pop('coded_label'))
        update_attributes(instance, validated_data)
        instance.save()

        if responsible_users_data:
            instance.responsible_users.clear()
            instance.responsible_users.add(*responsible_users_data)
        return instance

    @staticmethod
    def create_coded_cause_label(coded_label_data):
        coded_label_data['tenant'] = coded_label_data['tenant'].pk
        serializer = CodedCauseLabelSerializer(data=coded_label_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.instance

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
