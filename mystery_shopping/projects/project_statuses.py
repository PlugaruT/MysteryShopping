class ProjectStatus:
    PLANNED = 'planned'
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    REVIEWED = 'reviewed'
    APPROVED = 'approved'
    DECLINED = 'declined'
    REJECTED = 'rejected'

    EDITABLE_STATUSES = [PLANNED, DRAFT, DECLINED]
