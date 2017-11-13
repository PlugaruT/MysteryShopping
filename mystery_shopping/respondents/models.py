from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_fsm import FSMField, transition, RETURN_VALUE
from model_utils import Choices
from model_utils.models import TimeStampedModel

from mystery_shopping.common.models import Tag, ModelEnum
from mystery_shopping.projects.models import Evaluation
from mystery_shopping.respondents.managers import RespondentCaseQuerySet, RespondentQuerySet
from mystery_shopping.users.models import ClientUser, User


class Respondent(models.Model):
    """
        Model for storing information about detractors of an evaluation.
    """
    name = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    comment = models.CharField(max_length=400, blank=True)
    additional_comment = models.CharField(max_length=400, blank=True)
    phone = models.CharField(blank=True, max_length=15)
    status_choices = Choices(('TO_CONTACT', 'To Contact'),
                             ('CALL_BACK', 'Call Back'),
                             ('CONTACTED', 'Contacted'))
    status = models.CharField(max_length=11, choices=status_choices, default='TO_CONTACT')

    evaluation = models.ForeignKey(Evaluation, related_name='detractors', null=True)
    number_of_questions = models.IntegerField(default=0)

    objects = RespondentQuerySet.as_manager()

    def __str__(self):
        return u'{} {}'.format(self.name, self.surname)

    def get_detractor_questions(self):
        return self.evaluation.questionnaire.get_indicator_questions()

    def get_visited_place(self):
        return self.evaluation.company_element

    def get_current_case(self):
        if self.respondent_cases.count() > 0:
            return self.respondent_cases[0]
        return None


class RespondentCaseState(ModelEnum):
    INIT = 'INIT'
    ASSIGNED = 'ASSIGNED'
    ESCALATED = 'ESCALATED'
    ANALYSIS = 'ANAL'  # just because we can
    IMPLEMENTATION = 'IMPLEMENTATION'
    FOLLOW_UP = 'FOLLOW_UP'
    SOLVED = 'SOLVED'
    CLOSED = 'CLOSED'


class RespondentCase(TimeStampedModel):
    """
    A solvable case that is opened for a respondent
    """

    ISSUE_TAG_TYPE = 'RESPONDENT_CASE_ISSUE'
    SOLUTION_TAG_TYPE = 'RESPONDENT_CASE_SOLUTION'
    FOLLOW_UP_TAG_TYPE = 'RESPONDENT_CASE_FOLLOW_UP'

    STATE_CHOICES = Choices(
        (RespondentCaseState.INIT, 'Init'),
        (RespondentCaseState.ASSIGNED, 'Assigned'),
        (RespondentCaseState.ESCALATED, 'Escalated'),
        (RespondentCaseState.ANALYSIS, 'Analysis'),
        (RespondentCaseState.IMPLEMENTATION, 'Implementation'),
        (RespondentCaseState.FOLLOW_UP, 'Follow up'),
        (RespondentCaseState.SOLVED, 'Solved'),
        (RespondentCaseState.CLOSED, 'Closed'),
    )

    respondent = models.ForeignKey(Respondent, related_name='respondent_cases', related_query_name='respondent_cases')
    responsible_user = models.ForeignKey(User, null=True, blank=True,
                                         related_name='respondent_cases_responsible_for',
                                         related_query_name='respondent_cases_responsible_for')

    issue = models.TextField(null=True, blank=True)
    issue_tags = models.ManyToManyField(Tag, blank=True,
                                        related_name='issue_respondent_cases',
                                        related_query_name='issue_respondent_cases')

    solution = models.TextField(null=True, blank=True)
    solution_tags = models.ManyToManyField(Tag, blank=True,
                                           related_name='solution_respondent_cases',
                                           related_query_name='solution_respondent_cases')

    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_user = models.ForeignKey(User, null=True, blank=True,
                                       related_name='respondent_cases_to_follow_up',
                                       related_query_name='respondent_cases_to_follow_up')
    follow_up = models.TextField(null=True, blank=True)
    follow_up_tags = models.ManyToManyField(Tag, blank=True,
                                            related_name='follow_up_respondent_cases',
                                            related_query_name='follow_up_respondent_cases')

    state = FSMField(choices=STATE_CHOICES, default=RespondentCaseState.INIT)

    objects = RespondentCaseQuerySet.as_manager()

    class Meta:
        default_related_name = 'respondent_cases'

    @staticmethod
    def _update_tags(tags, tag_names, get_or_create_func):
        tags.clear()
        if tag_names:
            if not isinstance(tag_names, (list, tuple, set)):
                tag_names = (tag_names,)

            for tag_name in tag_names:
                tag = get_or_create_func(tag_name)
                tags.add(tag)

    def _add_comment(self, message, user, state):
        RespondentCaseComment.objects.create(author=user, text=message, case_state=state, respondent_case=self)

    @transition(field=state, source=(RespondentCaseState.ASSIGNED, RespondentCaseState.ANALYSIS, RespondentCaseState.IMPLEMENTATION), target=RespondentCaseState.ESCALATED)
    def escalate(self, reason):
        self._add_comment(reason, self.responsible_user, RespondentCaseState.ESCALATED)

    @transition(field=state, source=(RespondentCaseState.INIT, RespondentCaseState.ESCALATED), target=RespondentCaseState.ASSIGNED)
    def assign(self, to, comment=None, user=None):
        if comment:
            self._add_comment(comment, user, RespondentCaseState.ASSIGNED)
        self.responsible_user = to

    @transition(field=state, source=RespondentCaseState.ASSIGNED, target=RespondentCaseState.ANALYSIS)
    def start_analysis(self):
        pass

    @transition(field=state, source=RespondentCaseState.ANALYSIS, target=RespondentCaseState.IMPLEMENTATION)
    def analyse(self, issue, issue_tags=None):
        self.issue = issue
        self.issue_tags.clear()
        self.issue_tags.add(*Tag.objects.get_or_create_all(self.ISSUE_TAG_TYPE, issue_tags))

    @transition(field=state, source=RespondentCaseState.IMPLEMENTATION, target=RETURN_VALUE(RespondentCaseState.FOLLOW_UP, RespondentCaseState.SOLVED))
    def implement(self, solution, solution_tags=None, follow_up_date=None, follow_up_user=None):
        self.solution = solution
        self.solution_tags.clear()
        self.solution_tags.add(*Tag.objects.get_or_create_all(self.SOLUTION_TAG_TYPE, solution_tags))

        if follow_up_date:
            self.follow_up_date = follow_up_date
            self.follow_up_user = follow_up_user if follow_up_user else self.responsible_user
            return RespondentCaseState.FOLLOW_UP
        else:
            return RespondentCaseState.SOLVED

    @transition(field=state, source=RespondentCaseState.FOLLOW_UP, target=RespondentCaseState.SOLVED)
    def follow_up(self, follow_up, follow_up_tags=None):
        self.follow_up = follow_up
        self.follow_up_tags.clear()
        self.follow_up_tags.add(*Tag.objects.get_or_create_all(self.FOLLOW_UP_TAG_TYPE, follow_up_tags))

    @transition(field=state, target=RespondentCaseState.CLOSED)
    def close(self, reason, user=None):
        user = user if user else self.responsible_user
        self._add_comment(reason, user, RespondentCaseState.CLOSED)


class RespondentCaseComment(models.Model):
    """
    A comment in a respondent case
    """
    respondent_case = models.ForeignKey(RespondentCase, related_name='comments')

    author = models.ForeignKey(User)
    text = models.TextField()
    case_state = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'date'
        ordering = ('date',)
