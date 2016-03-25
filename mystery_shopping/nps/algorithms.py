from collections import defaultdict

from mystery_shopping.questionnaires.constants import IndicatorQuestionType


def get_nps_marks(questionnaire_list, indicator_type):
    indicator_scores = list()
    for questionnaire in questionnaire_list:
        for question in questionnaire.questions.all():
            if question.type in {indicator_type, }:
                indicator_scores.append(question.score)
    return indicator_scores


def calculate_indicator_score(nps_marks):

    if len(nps_marks) == 0:
        return None, None, None, None

    detractors_marks = []
    passives_marks = []
    promoters_marks = []

    for mark in nps_marks:
        mark = int(mark)
        if mark < 7:
            detractors_marks.append(mark)
        elif mark < 9:
            passives_marks.append(mark)
        else:
            promoters_marks.append(mark)

    total_marks = float(len(nps_marks))

    detractors_percentage = len(detractors_marks) / total_marks * 100
    passives_percentage = len(passives_marks) / total_marks * 100
    promoters_percentage = len(promoters_marks) / total_marks * 100

    indicator_score = promoters_percentage - detractors_percentage

    score = dict()
    score['indicator'] = round(indicator_score, 2)
    score['promoters'] = round(promoters_percentage, 2)
    score['passives'] = round(passives_percentage, 2)
    score['detractors'] = round(detractors_percentage, 2)
    return score


def group_questions_by_answer(questionnaire_list, indicator_type):
    """

    :param questionnaire_list:
    :param indicator_type:
    :return:
    """
    indicator_details = defaultdict(lambda: defaultdict(list))
    for questionnaire in questionnaire_list:
        questionnaire_indicator_score = questionnaire.questions.filter(type=indicator_type).first()
        if questionnaire_indicator_score:
            for question in questionnaire.questions.all():
                if question.type not in IndicatorQuestionType.INDICATORS_LIST:
                    indicator_details[question.question_body][question.answer].append(
                        questionnaire_indicator_score.score)

    return indicator_details


def get_indicator_details(questionnaire_list, indicator_type):
    details = list()
    nps_categories = group_questions_by_answer(questionnaire_list, indicator_type)

    for item_label, responses in nps_categories.items():
        detail_item = dict()
        detail_item['results'] = list()

        for answer_choice in responses:
            answer_choice_result = dict()
            answer_choice_result['choice'] = answer_choice
            answer_choice_result['score'] = calculate_indicator_score(responses[answer_choice])
            answer_choice_result['number_of_respondents'] = len(responses[answer_choice])
            detail_item['results'].append(answer_choice_result)

        detail_item['item_label'] = item_label
        details.append(detail_item)

    return details