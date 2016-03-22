from collections import defaultdict


# def separate_causes(questionnaire_template):
#     appreciation_causes = defaultdict(list)
#     frustration_causes = defaultdict(list)
#     for questionnaire in questionnaire_template.questionnaires.all():
#         for question in questionnaire.questions.all():
#             if question.type == 'n' and question.order == 1:
#                 if question.score > 8:
#                     appreciation_causes[question.question_body]

def get_nps_marks(questionnaire_template):
    nps_dict = defaultdict(list)
    for questionnaire in questionnaire_template.questionnaires.all():
        for question in questionnaire.questions.all():
            if question.type == 'n':
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

    return nps_score, promoters_percentage, passives_percentage, detractors_percentage
