# dict for mapping respondents type
# detractors, passive and promoters are only to NPS indicator
# for other indicators use provided alternatives
from model_utils import Choices

RESPONDENTS_MAPPING = {
    'DETRACTOR': 'NEGATIVE',
    'PASSIVE': 'NEUTRAL',
    'PROMOTERS': 'POSITIVE'
}


class RespondentCaseState:
    INIT = 'INIT'
    ASSIGNED = 'ASSIGNED'
    ESCALATED = 'ESCALATED'
    ANALYSIS = 'ANAL'  # just because we can
    IMPLEMENTATION = 'IMPLEMENTATION'
    PLANNED_FOR_FOLLOW_UP = 'PLANNED_FOR_FOLLOW_UP'
    FOLLOW_UP = 'FOLLOW_UP'
    SOLVED = 'SOLVED'
    CLOSED = 'CLOSED'

    STATE_CHOICES = Choices(
        (INIT, 'Init'),
        (ASSIGNED, 'Assigned'),
        (ESCALATED, 'Escalated'),
        (ANALYSIS, 'Analysis'),
        (IMPLEMENTATION, 'Implementation'),
        (FOLLOW_UP, 'Follow up'),
        (PLANNED_FOR_FOLLOW_UP, 'Planned for follow up'),
        (SOLVED, 'Solved'),
        (CLOSED, 'Closed'),
    )

    ACTIVE_STATES = [ASSIGNED, ESCALATED, ANALYSIS, IMPLEMENTATION, FOLLOW_UP]
    ALL_STATES = ACTIVE_STATES + [SOLVED, CLOSED]
