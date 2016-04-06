from collections import defaultdict

from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.questionnaires.constants import IndicatorQuestionType
from mystery_shopping.projects.models import Entity
from mystery_shopping.nps.models import CodedCause
from mystery_shopping.nps.serializers import CodedCauseSerializer


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
        score['indicator'] = None
        score['promoters'] = None
        score['passives'] = None
        score['detractors'] = None
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


def group_questions_by_pos(questionnaire_list, indicator_type):
    indicator_pos_details = defaultdict(lambda :defaultdict(list))
    for questionnaire in questionnaire_list:
        questionnaire_indicator_score = questionnaire.questions.filter(type=indicator_type).first()
        if questionnaire_indicator_score:

            indicator_pos_details['entities'][questionnaire.evaluation.entity.name].append(questionnaire_indicator_score.score)
            if questionnaire.evaluation.section is not None:
                indicator_pos_details['sections'][questionnaire.evaluation.section.name].append(questionnaire_indicator_score.score)

    return indicator_pos_details


def create_details_skeleton(questionnaire_template):
    """
    Initialize structure of dict to contain all question choices

    :param questionnaire_template: Template Questionnaire to extract the choices from
    :return: initial structure of the indicator details
    """
    indicator_skeleton = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for question in questionnaire_template.template_questions.all():
        for question_choice in question.template_question_choices.all():
            indicator_skeleton[question.question_body][question_choice.text]['other_choices'] = []
            indicator_skeleton[question.question_body][question_choice.text]['marks'] = []
    return indicator_skeleton


def get_indicator_details(questionnaire_list, indicator_type):
    """
    Collect detailed data about inticator_type

    :param questionnaire_list:
    :param indicator_type:
    :return: the indicator scores
    """
    details = list()
    indicator_skeleton = create_details_skeleton(questionnaire_list.first().template)
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

    indicators_per_pos = group_questions_by_pos(questionnaire_list, indicator_type)

    for pos_type in indicators_per_pos:
        if pos_type is not 'sections':
            detail_item = defaultdict(list)
            detail_item['results'] = list()
            detail_item['item_label'] = pos_type.capitalize()
            for entity, marks in indicators_per_pos[pos_type].items():
                pos_detail = dict()
                pos_detail['choice'] = entity
                pos_detail['score'] = calculate_indicator_score(marks)
                pos_detail['number_of_respondents'] = len(marks)
                pos_detail['other_answer_choices'] = list()
                detail_item['results'].append(pos_detail)

            details.append(detail_item)

    return details


def calculate_overview_score(questionnaire_list):
    overview_list = dict()
    for indicator_type in IndicatorQuestionType.INDICATORS_LIST:
        indicator_list = get_indicator_scores(questionnaire_list, indicator_type)
        overview_list[indicator_type] = calculate_indicator_score(indicator_list)

    return overview_list


def sort_question_by_coded_cause(questionnaire_list, indicator_type):
    coded_causes_dict = defaultdict(list)
    coded_causes_response = list()

    for questionnaire in questionnaire_list:
        indicator_question = questionnaire.questions.filter(type=indicator_type).first()
        if indicator_question.coded_causes.first():
            coded_causes_dict[indicator_question.coded_causes.first().id].append(indicator_question.id)
        else:
            coded_causes_dict['unsorted'].append(indicator_question.id)

    for coded_cause in coded_causes_dict:
        temp_dict = dict()
        if coded_cause != 'unsorted':
            coded_cause_inst = CodedCause.objects.get(pk=coded_cause)
            coded_cause_serialized = CodedCauseSerializer(coded_cause_inst)
            temp_dict['coded_cause'] = coded_cause_serialized.data
            temp_dict['count'] = len(coded_causes_dict[coded_cause])
            coded_causes_response.append(temp_dict)
        else:
            temp_dict['coded_cause'] = coded_cause
            temp_dict['count'] = len(coded_causes_dict[coded_cause])
            coded_causes_response.append(temp_dict)
    return coded_causes_response


def collect_data_for_indicator_dashboard(project, entity_id, indicator_type):
    try:
        entity = Entity.objects.get(pk=entity_id)
    except Entity.DoesNotExist:
        entity = None

    questionnaire_list = Questionnaire.objects.get_project_questionnaires(project, entity)
    indicator_question = None

    # Extract the question with the desired indicator (if questionnaires exist)
    if questionnaire_list:
        indicator_question = questionnaire_list.first().get_indicator_question(indicator_type)

    response = dict()
    if indicator_question:
        # Get all the questionnaires from the requested project
        indicator_list = get_indicator_scores(questionnaire_list, indicator_type)
        response['general'] = calculate_indicator_score(indicator_list)

        response['details'] = get_indicator_details(questionnaire_list, indicator_type)

        response['coded_causes'] = sort_question_by_coded_cause(questionnaire_list, indicator_type)
    else:
        response['general'] = calculate_indicator_score([])

        response['details'] = []

        response['coded_causes'] = []

    return response


def collect_data_for_overview_dashboard(project, entity_id):
    try:
        entity = Entity.objects.get(pk=entity_id)
    except Entity.DoesNotExist:
        entity = None

    questionnaire_list = Questionnaire.objects.get_project_questionnaires(project, entity)

    return calculate_overview_score(questionnaire_list)
