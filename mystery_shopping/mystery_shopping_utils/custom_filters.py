from django.db.models.query_utils import Q
import django_filters


class DetractorIndicatorMultipleChoiceFilter(django_filters.rest_framework.AllValuesMultipleFilter):
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

    def filter_detractors(self, qs, questionnaires):
        return qs.filter(evaluation__questionnaire__in=questionnaires)
