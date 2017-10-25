from enum import Enum


class EvaluationStatus:
    PLANNED = 'planned'
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    REVIEWED = 'reviewed'
    APPROVED = 'approved'
    DECLINED = 'declined'
    REJECTED = 'rejected'

    EDITABLE_STATUSES = [PLANNED, DRAFT, DECLINED]


class ProjectType:
    MYSTERY_SHOPPING = 'm'
    CUSTOMER_EXPERIENCE_INDEX = 'c'


class RespondentType(Enum):
    """
    class that holds information about the scores that define each respondent type
    Detractors are from 0 to 6
    Passive are 7 and 8
    Promoters are 9 and 10
    """
    DETRACTOR_LOW = 0
    DETRACTOR_HIGH = 6

    PASSIVE_LOW = 7
    PASSIVE_HIGH = 8

    PROMOTER_LOW = 9
    PROMOTER_HIGH = 10
