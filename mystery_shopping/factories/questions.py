from factory import DjangoModelFactory

from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.models import QuestionnaireQuestion


class IndicatorQuestionFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireQuestion
    type = QuestionType.INDICATOR_QUESTION
