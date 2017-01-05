from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_condition import Or

from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.questionnaires.models import QuestionnaireTemplateStatus
from .models import QuestionnaireScript
from .models import Questionnaire
from .models import QuestionnaireTemplate
from .models import QuestionnaireBlock
from .models import QuestionnaireTemplateBlock
from .models import QuestionnaireQuestion
from .models import QuestionnaireTemplateQuestion
from .models import QuestionnaireQuestionChoice
from .models import QuestionnaireTemplateQuestionChoice
from .models import CrossIndexTemplate
from .models import CrossIndex
from .serializers import QuestionnaireScriptSerializer
from .serializers import QuestionnaireSerializer
from .serializers import QuestionnaireTemplateSerializer
from .serializers import QuestionnaireBlockSerializer
from .serializers import QuestionnaireTemplateBlockSerializer
from .serializers import QuestionnaireQuestionSerializer
from .serializers import QuestionnaireTemplateQuestionSerializer
from .serializers import QuestionnaireQuestionChoiceSerializer
from .serializers import QuestionnaireTemplateQuestionChoiceSerializer
from .serializers import CrossIndexTemplateSerializer
from .serializers import CrossIndexSerializer
from .serializers import QuestionnaireSimpleSerializer
from .serializers import QuestionSimpleSerializer
from .serializers import BlockSimpleSerializer

from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant


class QuestionnaireScriptViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireScript.objects.all()
    serializer_class = QuestionnaireScriptSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplate.objects.all()
    serializer_class = QuestionnaireTemplateSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)
    filter_backends = (TenantFilter,)

    def get_queryset(self):
        """
        Filter queryset by Questionnaire type ('c' or 'm') and by Tenant the user belongs to.
        """
        questionnaire_type = self.request.query_params.get('type', 'm')
        queryset = self.queryset.filter(type=questionnaire_type)
        queryset = self.serializer_class.setup_eager_loading(queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        questionnaire_status = QuestionnaireTemplateStatus.objects.create()
        request.data['tenant'] = request.user.tenant.id
        request.data['created_by'] = request.user.id
        request.data['status'] = questionnaire_status.id
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def get_archived(self, request):
        queryset = self.queryset.filter(is_archived=True)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def get_unarchived(self, request):
        queryset = self.queryset.filter(is_archived=False)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['put'])
    def archive(self, request, pk=None):
        questionnaire = get_object_or_404(QuestionnaireTemplate, pk=pk)
        questionnaire.archive(request.user)
        questionnaire.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['put'])
    def unarchive(self, request, pk=None):
        questionnaire = get_object_or_404(QuestionnaireTemplate, pk=pk)
        questionnaire.unarchive(request.user)
        questionnaire.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        template_questionnaire = get_object_or_404(QuestionnaireTemplate, pk=pk)
        new_title = request.data.get('title')
        self.assign_new_title_and_make_it_editable(template_questionnaire, new_title)
        cloned_template_questionnaire = self._clone_questionnaire_template(template_questionnaire)
        cloned_template_questionnaire_serialized = QuestionnaireTemplateSerializer(data=cloned_template_questionnaire)
        cloned_template_questionnaire_serialized.is_valid(raise_exception=True)
        cloned_template_questionnaire_serialized.save()
        return Response(data=cloned_template_questionnaire_serialized.data, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def assign_new_title_and_make_it_editable(questionnaire, new_title):
        questionnaire.title = new_title if new_title else questionnaire.title + ' (Copy)'
        questionnaire.is_editable = True

    @staticmethod
    def _clone_questionnaire_template(questionnaire_template):
        questionnaire_status = QuestionnaireTemplateStatus.objects.create()
        questionnaire_template_serialized = QuestionnaireTemplateSerializer(questionnaire_template)
        questionnaire_template_serialized = dict(questionnaire_template_serialized.data)
        questionnaire_template_serialized.pop('id')
        questionnaire_template_serialized.pop('status_repr')
        questionnaire_template_serialized['status'] = questionnaire_status.id
        return questionnaire_template_serialized


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Questionnaire.objects.all()
        queryset = self.serializer_class.setup_eager_loading(queryset)
        return queryset


class QuestionnaireTemplateBlockViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateBlock.objects.all()
    serializer_class = QuestionnaireTemplateBlockSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)

    def destroy(self, request, pk=None):
        queryset = QuestionnaireTemplateBlock.objects.filter(pk=pk)
        template_block = get_object_or_404(queryset, pk=pk)
        siblings_to_update = template_block.get_siblings().filter(questionnaire_template=template_block.questionnaire_template, order__gt=template_block.order)
        # update 'order' field of sibling blocks when a block gets deleted
        for sibling in siblings_to_update:
            sibling.order -= 1
            sibling.save()

        template_block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QuestionnaireBlockViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireBlock.objects.all()
    serializer_class = QuestionnaireBlockSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireTemplateQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateQuestion.objects.all()
    serializer_class = QuestionnaireTemplateQuestionSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def destroy(self, request, pk=None):
        queryset = QuestionnaireTemplateQuestion.objects.filter(pk=pk)
        template_question = get_object_or_404(queryset, pk=pk)
        questions_to_update = QuestionnaireTemplateQuestion.objects.filter(template_block=template_question.template_block, order__gt=template_question.order)
        for question in questions_to_update:
            question.order -= 1
            question.save()

        template_question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['put'], url_path='review-weights')
    def review_weights(self, request, pk=None):
        """
        Endpoint for updating the weights of questions (even after the questionnaires is flagged as non-editable if it's a CXI project)
        :param request: request with the question info and siblings' info (other questions' weights)
        :param pk: pk of the questions
        :return: status code ok
        """

        template_question = QuestionnaireTemplateQuestion.objects.is_question_editable(pk)

        if template_question is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        new_weight = request.data.get('weight')

        if new_weight is not None:
            template_question.weight = new_weight

        siblings = request.data.get('siblings', [])
        template_question.update_siblings(siblings, template_question.template_block)

        template_question.save()
        return Response(status=status.HTTP_200_OK)


class QuestionnaireQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireQuestion.objects.all()
    serializer_class = QuestionnaireQuestionSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireTemplateQuestionChoiceViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateQuestionChoice.objects.all()
    serializer_class = QuestionnaireTemplateQuestionChoiceSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def destroy(self, request, pk=None):
        queryset = QuestionnaireTemplateQuestionChoice.objects.filter(pk=pk)
        template_question_choice = get_object_or_404(queryset, pk=pk)
        choice_to_update = QuestionnaireTemplateQuestionChoice.objects.filter(template_question=template_question_choice.template_question, order__gt=template_question_choice.order)
        for choice in choice_to_update:
            choice.order -= 1
            choice.save()

        template_question_choice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QuestionnaireQuestionChoiceViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireQuestionChoice.objects.all()
    serializer_class = QuestionnaireQuestionChoiceSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class CrossIndexTemplateViewSet(viewsets.ModelViewSet):
    queryset = CrossIndexTemplate.objects.all()
    serializer_class = CrossIndexTemplateSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class CrossIndexViewSet(viewsets.ModelViewSet):
    queryset = CrossIndex.objects.all()
    serializer_class = CrossIndexSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireSimpleViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSimpleSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Questionnaire.objects.all()
        queryset = self.serializer_class.setup_eager_loading(queryset)
        return queryset


class QuestionSimpleViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireQuestion.objects.all()
    serializer_class = QuestionSimpleSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class BlockSimpleViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireBlock.objects.all()
    serializer_class = BlockSimpleSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)
