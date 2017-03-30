from django.db.models import Sum, IntegerField, Case, When


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
