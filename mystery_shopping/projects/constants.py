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
