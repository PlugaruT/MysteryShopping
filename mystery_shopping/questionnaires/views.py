from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_condition import Or

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

from mystery_shopping.projects.models import Project
from mystery_shopping.cxi.serializers import QuestionnaireQuestionToEncodeSerializer


class QuestionnaireScriptViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireScript.objects.all()
    serializer_class = QuestionnaireScriptSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplate.objects.all()
    serializer_class = QuestionnaireTemplateSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        """Filter queryset by Questionnaire type ('c' or 'm') and by Tenant the user belongs to.
        """
        queryset = self.queryset.all()
        questionnaire_type = self.request.query_params.get('type', 'm')
        questionnaire_type = questionnaire_type[0] if isinstance(questionnaire_type, list) else questionnaire_type
        queryset = queryset.filter(type=questionnaire_type, tenant=self.request.user.tenant)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def get_archived(self, request):
        queryset = self.queryset.filter(is_archived=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def get_unarchived(self, request):
        queryset = self.queryset.filter(is_archived=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['put'])
    def archive(self, request, pk=None):
        questionnaire = get_object_or_404(QuestionnaireTemplate, pk=pk)
        questionnaire.archive()
        questionnaire.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['put'])
    def unarchive(self, request, pk=None):
        questionnaire = get_object_or_404(QuestionnaireTemplate, pk=pk)
        questionnaire.unarchive()
        questionnaire.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Questionnaire.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
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


class QuestionnaireQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireQuestion.objects.all()
    serializer_class = QuestionnaireQuestionSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)
    encode_serializer_class = QuestionnaireQuestionToEncodeSerializer

    @list_route(['GET', 'PUT'])
    def encode(self, request):
        project_id = request.query_params.get('project', None)
        if project_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'Project does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.user.tenant != project.tenant:
            return Response({'detail': 'You do not have access to this project'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            questions = QuestionnaireQuestion.objects.get_project_questions(project_id)

            serializer = self.encode_serializer_class(questions, many=True)

        elif request.method == 'PUT':
            question_changes = {x['id']: x.get('coded_causes', [None])[0] for x in request.data}
            questions = QuestionnaireQuestion.objects.filter(pk__in=question_changes.keys(),
                                                             questionnaire__evaluation__project=project_id)
            for question in questions:
                question.coded_causes.clear()
                coded_cause_id = question_changes[question.id]
                if coded_cause_id:
                    question.coded_causes.add(coded_cause_id)

            return Response('', status=status.HTTP_200_OK)

        else:
            pass

        return Response(serializer.data, status=status.HTTP_200_OK)


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
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class QuestionSimpleViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireQuestion.objects.all()
    serializer_class = QuestionSimpleSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class BlockSimpleViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireBlock.objects.all()
    serializer_class = BlockSimpleSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)
