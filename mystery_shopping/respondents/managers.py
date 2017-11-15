from collections import defaultdict
from django.utils.timezone import now
from django.db.models import QuerySet
from django.db.models.aggregates import Count
from django_fsm_log.models import StateLog

from mystery_shopping.common.iterators import pairs


class RespondentCaseQuerySet(QuerySet):

    @staticmethod
    def _time_delta(current_log, next_log):
        if next_log is None or next_log['object_id'] != current_log['object_id']:
            next_time = now()
        else:
            next_time = next_log['timestamp']

        return (next_time - current_log['timestamp']).seconds

    @classmethod
    def _avg_time_per_state(cls, state_logs, transition_states):
        states_sum = defaultdict(lambda: 0)
        states_count = defaultdict(lambda: 0)
        for curr, nxt in pairs(state_logs):
            if curr['state'] in transition_states:
                state = curr['state']
                states_sum[state] += cls._time_delta(curr, nxt)
                states_count[state] += 1

        for state in transition_states:
            avg_time = int(states_sum[state] / states_count[state]) if states_count[state] > 0 else 0
            yield (state, avg_time)

    def get_average_time_per_state(self, project_id):
        project_cases = self.filter(respondent__evaluation__project_id=project_id).order_by('id').values('id')
        state_logs = (StateLog.objects.filter(object_id__in=project_cases)
                      .order_by('object_id', 'timestamp')
                      .values('timestamp', 'state', 'object_id'))

        transition_states = ['ASSIGNED', 'ESCALATED', 'ANAL', 'IMPLEMENTATION', 'FOLLOW_UP']
        response = []

        for state, avg_time in self._avg_time_per_state(state_logs, transition_states):
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
