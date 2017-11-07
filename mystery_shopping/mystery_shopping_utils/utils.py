from django.db.models import Sum, IntegerField, Case, When

from mystery_shopping.projects.constants import RespondentType


def calculate_percentage(nominator, denominator, round_to=2):
    """
    helper method for calculating the percentage
    :param nominator: what to divide
    :param denominator: on what to divide
    :param round_to: how many digits after comma
    :return: float
    """
    if denominator <= 0:
        denominator = 1
    return round(nominator / denominator * 100, round_to)


def aggregate_questions_for_nps_indicator(questions_list):
    """
    :param questions_list: list of QuestionnaireQuestions to count number of respondents for NPS indicator
    :return: dict of the form
        {
            'DETRACTOR': 1224,
            'PASSIVE': 125,
            'PROMOTERS': 644
        }
    """
    return questions_list.aggregate(
        DETRACTOR=Sum(
            Case(
                When(score__lte=6, then=1),
                output_field=IntegerField()
            )
        ),
        PASSIVE=Sum(
            Case(
                When(score=7, then=1),
                When(score=8, then=1),
                output_field=IntegerField()
            )
        ),
        PROMOTERS=Sum(
            Case(
                When(score__gte=9, then=1),
                output_field=IntegerField()
            )
        )
    )


def aggregate_questions_for_other_indicators(questions_list):
    """
    :param questions_list: list of QuestionnaireQuestions to count number of respondents for other indicators
    :return: dict of the form
        {
            'NEGATIVE': 1224,
            'NEUTRAL': 125,
            'POSITIVE': 644
        }
    """
    return questions_list.aggregate(
        NEGATIVE=Sum(
            Case(
                When(score__lte=6, then=1),
                output_field=IntegerField()
            )
        ),
        NEUTRAL=Sum(
            Case(
                When(score=7, then=1),
                When(score=8, then=1),
                output_field=IntegerField()
            )
        ),
        POSITIVE=Sum(
            Case(
                When(score__gte=9, then=1),
                output_field=IntegerField()
            )
        )
    )


def modify_questions_body(questionnaire):
    questions = questionnaire.template_questions.all()

    for question in questions:
        new_body = ''
        print('Current question body is: {}'.format(question.question_body))
        new_body = input('New body: ')
        if new_body != '':
            question.question_body = new_body
            question.save()
            question.questions.update(question_body=new_body)


def remove_none_from_list(items):
    return [item for item in items if item is not None]


def is_detractor(score):
    return score <= RespondentType.DETRACTOR_HIGH.value


def is_passive(score):
    return score == RespondentType.PASSIVE_LOW.value or score == RespondentType.PASSIVE_HIGH.value


def is_promoter(score):
    return score >= RespondentType.PROMOTER_LOW.value


def count_detractors(scores):
    return sum(is_detractor(score) for score in scores)


def count_passives(scores):
    return sum(is_passive(score) for score in scores)


def count_promoters(scores):
    return sum(is_promoter(score) for score in scores)


def flatten_list_of_lists(list_of_lists):
    return [y for x in list_of_lists for y in x]
