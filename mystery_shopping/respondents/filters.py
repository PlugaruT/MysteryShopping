from django.db.models.query_utils import Q
from django_filters import AllValuesMultipleFilter, DateFromToRangeFilter, ModelMultipleChoiceFilter, rest_framework

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.respondents.models import Respondent


class RespondentFilter(rest_framework.FilterSet):
    places = ModelMultipleChoiceFilter(queryset=CompanyElement.objects.all(), name="evaluation__company_element")
    date = DateFromToRangeFilter(name="evaluation__time_accomplished", lookup_expr='date')
    questions = AllValuesMultipleFilter(name='number_of_questions')
    indicators = DetractorIndicatorMultipleChoiceFilter(name="evaluation__questionnaire__questions__additional_info",
                                                        conjoined=True,
                                                        query_manager=Questionnaire.objects.filter)

    class Meta:
        model = Respondent
        fields = ['date', 'places', 'status', 'questions', 'indicators']


class DetractorIndicatorMultipleChoiceFilter(rest_framework.AllValuesMultipleFilter):
    """
    Filter to get detractors only for the given indicator (types).
    Since the `qs` is already filtered by project, we can just filter out the detractors
    that have the corresponding (<= 6) score and indicators.

    (sending the Questionnaire model filter as `query_manager` attribute, so I don't have to
    import it here (and some more decoupling),
    but still keeping it pretty specific. If need be, will "modularize" it more with
    sending it look_up fields and stuff.
    """

    def __init__(self, *args, **kwargs):
        try:
            self.query_manager = kwargs.pop('query_manager')
        except KeyError as key:
            raise Exception('Missing {} argument. Please define it.'.format(key))
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        if not self.conjoined:
            q = Q()

        for indicator in set(value):
            predicate = self.get_filter_predicate(indicator)
            if self.conjoined:
                questionnaires = self.query_manager(predicate)
                qs = self.filter_detractors(qs, questionnaires)
            else:
                q |= predicate

        if not self.conjoined:
            questionnaires = self.query_manager(q)
            qs = self.filter_detractors(qs, questionnaires)

        return qs.distinct() if self.distinct else qs

    def get_filter_predicate(self, indicator):
        return Q(questions__additional_info=indicator, questions__score__lte=6)

    @staticmethod
    def filter_detractors(qs, questionnaires):
        return qs.filter(evaluation__questionnaire__in=questionnaires)
