from django.db.models import QuerySet
from django.db.models.aggregates import Count
from django_fsm_log.models import StateLog


class RespondentCaseQuerySet(QuerySet):
    def get_average_time_per_state(self, project_id):
        project_cases = self.filter(respondent__evaluation__project_id=project_id).order_by('id').values('id')
        state_logs = (StateLog.objects.filter(object_id__in=project_cases)
                      .order_by('object_id', 'timestamp')
                      .values('timestamp', 'state', 'object_id'))

        transition_states = ['ASSIGNED', 'ESCALATED', 'ANAL', 'IMPLEMENTATION', 'FOLLOW_UP']
        response = []

        for state in transition_states:
            avg_time = 0  # todo implement the avg calculation here
            item = {'state': state, 'avg_time': avg_time}
            response.append(item)

        return response

    def get_cases_per_state(self, project_id):
        """
        Method returns data about number of cases for each state. If the state doesn't have cases
        It will return that the state has 0
        :return: list of dicts
        """
        default_response = [
            {'state': 'ASSIGNED', 'count': 0},
            {'state': 'ESCALATED', 'count': 0},
            {'state': 'ANAL', 'count': 0},
            {'state': 'IMPLEMENTATION', 'count': 0},
            {'state': 'FOLLOW_UP', 'count': 0},
            {'state': 'SOLVED', 'count': 0},
            {'state': 'CLOSED', 'count': 0},
        ]
        result = list(
            self.filter(respondent__evaluation__project_id=project_id).values('state').annotate(count=Count('id'))
        )
        result.extend(list(filter(lambda d: d['state'] not in [d['state'] for d in result], default_response)))
        return result


class RespondentQuerySet(QuerySet):
    def without_cases(self):
        return self.annotate(cases_count=Count('respondent_cases')).filter(cases_count=0)

    def with_cases(self):
        return self.annotate(cases_count=Count('respondent_cases')).filter(cases_count__gt=0)
