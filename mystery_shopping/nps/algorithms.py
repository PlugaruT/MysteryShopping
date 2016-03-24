from collections import defaultdict

from mystery_shopping.questionnaires.constants import IndicatorQuestionType


def get_nps_marks(questionnaire_template):
    nps_dict = defaultdict(list)
    for questionnaire in questionnaire_template.questionnaires.all():
        for question in questionnaire.questions.all():
            if question.type in {IndicatorQuestionType.NPS_QUESTION, }:
                nps_dict['scores'].append(question.score)
    return nps_dict


def calculate_nps_score(nps_marks):

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

    nps_score = promoters_percentage - detractors_percentage

    return round(nps_score, 2),round(promoters_percentage, 2), round(passives_percentage, 2), round(detractors_percentage, 2)


def group_questions_by_answer(questionnaire_template, indicator_question):
    nps_details = defaultdict(lambda: defaultdict(list))
    for questionnaire in questionnaire_template.questionnaires.all():
        questionnaire_nps_score = questionnaire.questions.get(type=indicator_question)
        for question in questionnaire.questions.all():
            if question.type not in IndicatorQuestionType.INDICATORS_DICT:
                nps_details[question.question_body][question.answer].append(questionnaire_nps_score.score)

    return nps_details
