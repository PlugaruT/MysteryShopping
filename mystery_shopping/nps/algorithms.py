from collections import defaultdict

from mystery_shopping.questionnaires.constants import IndicatorQuestionType


def get_indicator_scores(questionnaire_list, indicator_type):
    """
    Returns a list of the indicator's marks

    :param questionnaire_list: list of questionnaires to get the indicator scores from
    :param indicator_type: can be 'n', 'j', 'e' or 'u'
    :return: a list with the indicator's marks
    """
    indicator_marks = list()
    for questionnaire in questionnaire_list:
        for question in questionnaire.questions.all():
            if question.type in {indicator_type, }:
                indicator_marks.append(question.score)
    return indicator_marks


def calculate_indicator_score(indicator_marks):
    """
    Calculates the detractors, promoters and passives scores for a given list of indicator scores

    :param indicator_marks: list of the indicator's scores
    :return: a dict with the 'indicator', 'promoters', 'detractors' and 'passives' keys, and scores respectively
    """
    if len(indicator_marks) == 0:
        score = dict()
        score['indicator'] = 0.0
        score['promoters'] = 0.0
        score['passives'] = 0.0
        score['detractors'] = 0.0
        return score

    detractors_marks = []
    passives_marks = []
    promoters_marks = []

    for score in indicator_marks:
        score = int(score)
        if score < 7:
            detractors_marks.append(score)
        elif score < 9:
            passives_marks.append(score)
        else:
            promoters_marks.append(score)

    indicator_scores_length = len(indicator_marks)

    detractors_percentage = len(detractors_marks) / indicator_scores_length * 100
    passives_percentage = len(passives_marks) / indicator_scores_length * 100
    promoters_percentage = len(promoters_marks) / indicator_scores_length * 100

    indicator_score = promoters_percentage - detractors_percentage

    score = dict()
    score['indicator'] = round(indicator_score, 2)
    score['promoters'] = round(promoters_percentage, 2)
    score['passives'] = round(passives_percentage, 2)
    score['detractors'] = round(detractors_percentage, 2)
    return score


def group_questions_by_answer(questionnaire_list, indicator_type, indicator_details):
    """

    :param questionnaire_list: list of questionnaires from which to group the indicator scores by answer
    :param indicator_type: can be 'n', 'j', 'e' or 'u'
    :return: the indicator's marks distributed per question choice selected
    :rtype: defaultdict
    """
    # indicator_details = defaultdict(lambda: defaultdict(list))
    for questionnaire in questionnaire_list:
        questionnaire_indicator_score = questionnaire.questions.filter(type=indicator_type).first()
        if questionnaire_indicator_score:
            for question in questionnaire.questions.all():
                if question.type not in IndicatorQuestionType.INDICATORS_LIST:
                    if question.answer_choices is not None:
                        indicator_details[question.question_body][question.answer]['marks'].append(questionnaire_indicator_score.score)
                    else:
                        indicator_details[question.question_body]['other']['marks'].append(questionnaire_indicator_score.score)
                        if question.answer.capitalize() not in indicator_details[question.question_body]['other']['other_choices']:
                            indicator_details[question.question_body]['other']['other_choices'].append(question.answer)

    return indicator_details


def create_details_skeleton(questionnaire_template):
    indicator_skeleton = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for question in questionnaire_template.template_questions.all():
        for question_choice in question.template_question_choices.all():
            indicator_skeleton[question.question_body][question_choice.text]['other_choices'] = []
            indicator_skeleton[question.question_body][question_choice.text]['marks'] = []
    return indicator_skeleton


def get_indicator_details(questionnaire_list, questionnaire_template, indicator_type):
    """

    :param questionnaire_list:
    :param indicator_type:
    :return: the indicator scores
    """
    details = list()
    indicator_skeleton = create_details_skeleton(questionnaire_template)
    indicator_categories = group_questions_by_answer(questionnaire_list, indicator_type, indicator_skeleton)

    for item_label, responses in indicator_categories.items():
        detail_item = dict()
        detail_item['results'] = list()

        for answer_choice in responses:
            answer_choice_result = dict()
            answer_choice_result['choice'] = answer_choice
            answer_choice_result['score'] = calculate_indicator_score(responses[answer_choice]['marks'])
            answer_choice_result['number_of_respondents'] = len(responses[answer_choice]['marks'])
            answer_choice_result['other_answer_choices'] = responses[answer_choice]['other_choices']
            detail_item['results'].append(answer_choice_result)

        detail_item['item_label'] = item_label
        details.append(detail_item)

    return details