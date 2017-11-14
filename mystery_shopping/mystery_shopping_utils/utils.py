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


def aggregate_respondents_distribution(questions_list):
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


def build_data_point(key, value, additional=0):
    """
    This method is going to be used when aggregating data for charts
    This represents a data point on the bar/pie/waterfall chart
    :param key: the name for what this data point represents
    :param value: value of the data point
    :param additional: additional info than can be used for different purposes
    :return: dict
    """
    return {
        'key': key,
        'value': value,
        'additional': additional
    }


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


def modify_questions_additional_info(questionnaire):
    questions = questionnaire.template_questions.all()

    for question in questions:
        print('Current question body is: {}'.format(question.question_body))
        print('Current question additional info is: {}'.format(question.additional_info))
        additional_info = input('New additional_info: ')
        if additional_info != '':
            question.additional_info = additional_info
            question.save()
            question.questions.update(additional_info=additional_info)


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
