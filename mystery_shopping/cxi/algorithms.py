from collections import defaultdict

from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.models import Questionnaire, QuestionnaireQuestion
from mystery_shopping.projects.models import Entity
from mystery_shopping.cxi.models import CodedCause
from mystery_shopping.cxi.models import ProjectComment
from mystery_shopping.cxi.serializers import CodedCauseSerializer
from mystery_shopping.cxi.serializers import ProjectCommentSerializer


def get_indicator_scores(questionnaire_list, indicator_type):
    """
    Returns a list of the indicator's marks

    :param questionnaire_list: list of questionnaires to get the indicator scores from
    :param indicator_type: can be anything
    :return: a list with the indicator's marks
    """
    indicator_marks = list()
    for questionnaire in questionnaire_list:
        for question in questionnaire.questions.all():
            if question.additional_info == indicator_type:
                indicator_marks.append(question.score)

    return indicator_marks


def calculate_indicator_score(indicator_marks):
    """
    Calculates the detractors, promoters and passives scores for a given list of indicator scores

    :param indicator_marks: list of the indicator's scores
    :return: a dict with the 'indicator', 'promoters', 'detractors' and 'passives' keys, and scores respectively
    """
    score = dict()
    if not indicator_marks:
        score['indicator'] = None
        score['promoters'] = None
        score['passives'] = None
        score['detractors'] = None
        return score

    detractors = 0
    passives = 0
    promoters = 0

    for mark in indicator_marks:
        if mark < 7:
            detractors += 1
        elif mark < 9:
            passives += 1
        else:
            promoters += 1

    indicator_marks_length = len(indicator_marks)

    detractors_percentage = detractors / indicator_marks_length * 100
    passives_percentage = passives / indicator_marks_length * 100
    promoters_percentage = promoters / indicator_marks_length * 100

    indicator_score = promoters_percentage - detractors_percentage

    score['indicator'] = round(indicator_score, 2)
    score['promoters'] = round(promoters_percentage, 2)
    score['passives'] = round(passives_percentage, 2)
    score['detractors'] = round(detractors_percentage, 2)
    return score


def sort_indicator_question_marks(indicator_dict, indicator_question, question):
    if question.type != QuestionType.INDICATOR_QUESTION:
        if question.answer_choices not in [None, []]:
            indicator_dict[question.question_body][question.answer]['marks'].append(indicator_question.score)
        else:
            indicator_dict[question.question_body]['other']['marks'].append(indicator_question.score)
            if question.answer.capitalize() not in indicator_dict[question.question_body]['other']['other_choices']:
                indicator_dict[question.question_body]['other']['other_choices'].append(question.answer)


def group_questions_by_answer(questionnaire_list, indicator_type, indicator_details):
    """
    :param questionnaire_list: list of questionnaires from which to group the indicator scores by answer
    :param indicator_type: can be anything
    :return: the indicator's marks distributed per question choice selected
    :rtype: defaultdict
    """

    coded_causes_dict = defaultdict(list)

    for questionnaire in questionnaire_list:
        questionnaire_indicator_question = questionnaire.questions.filter(
            type=QuestionType.INDICATOR_QUESTION,
            additional_info=indicator_type).first()

        if questionnaire_indicator_question:
            add_question_per_coded_cause(questionnaire_indicator_question, coded_causes_dict)

            for question in questionnaire.questions.all():
                sort_indicator_question_marks(indicator_details, questionnaire_indicator_question, question)

    return indicator_details, coded_causes_dict


def group_questions_by_pos(questionnaire_list, indicator_type):
    indicator_pos_details = defaultdict(lambda: defaultdict(list))
    for questionnaire in questionnaire_list:
        questionnaire_indicator_score = questionnaire.questions.filter(type=QuestionType.INDICATOR_QUESTION,
                                                                       additional_info=indicator_type).first()
        if questionnaire_indicator_score:
            indicator_pos_details['entities'][questionnaire.evaluation.entity.name].append(questionnaire_indicator_score.score)
            indicator_pos_details['ids'][questionnaire.evaluation.entity.name] = questionnaire.evaluation.entity.id
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


def sort_indicator_categories(details, indicator_categories):
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


def sort_indicators_per_pos(details, indicators):
    entity_key = 'entities'
    detail_item = defaultdict(list)
    detail_item['results'] = list()
    detail_item['item_label'] = entity_key.capitalize()
    for entity, marks in indicators.get(entity_key, {}).items():
        pos_detail = dict()
        pos_detail['choice'] = entity
        pos_detail['choice_id'] = indicators['ids'][entity]
        pos_detail['score'] = calculate_indicator_score(marks)
        pos_detail['number_of_respondents'] = len(marks)
        pos_detail['other_answer_choices'] = indicators['ids'][entity]
        detail_item['results'].append(pos_detail)
    details.append(detail_item)

    return details


def get_indicator_details(questionnaire_list, indicator_type):
    """
    Collect detailed data about inticator_type

    :param questionnaire_list:
    :param indicator_type:
    :return: the indicator scores
    """
    details = list()
    indicator_skeleton = create_details_skeleton(questionnaire_list.first().template)
    indicator_categories, coded_causes_dict = group_questions_by_answer(questionnaire_list, indicator_type, indicator_skeleton)
    sort_indicator_categories(details, indicator_categories)

    indicators_per_pos = group_questions_by_pos(questionnaire_list, indicator_type)
    sort_indicators_per_pos(details, indicators_per_pos)

    return_dict = dict()
    return_dict['details'] = details
    return_dict['coded_causes'] = sort_question_by_coded_cause(coded_causes_dict)
    return return_dict


def get_overview_project_comment(project, entity_id):
    project_comment = ProjectComment.objects.filter(project=project, entity=entity_id, indicator="").first()
    return None if project_comment is None else ProjectCommentSerializer(project_comment).data


def get_indicator_project_comment(project, entity_id, indicator_type):
    project_comment = ProjectComment.objects.filter(project=project, entity=entity_id, indicator=indicator_type).first()
    return None if project_comment is None else ProjectCommentSerializer(project_comment).data


def calculate_overview_score(questionnaire_list, project, entity_id):
    overview_list = dict()
    overview_list['indicators'] = dict()
    indicator_types_set = set()
    indicator_order = dict()
    for questionnaire in questionnaire_list:
        for indicator_question in questionnaire.questions.filter(type=QuestionType.INDICATOR_QUESTION).all():
            indicator_order[indicator_question.additional_info] = indicator_question.order
            indicator_types_set.add(indicator_question.additional_info)
    for indicator_type in indicator_types_set:
        indicator_list = get_indicator_scores(questionnaire_list, indicator_type)
        overview_list['indicators'][indicator_type] = calculate_indicator_score(indicator_list)
        overview_list['indicators'][indicator_type]['order'] = indicator_order[indicator_type]

    overview_list['project_comment'] = get_overview_project_comment(project, entity_id)
    return overview_list


def add_question_per_coded_cause(indicator_question, coded_cause_dict):
    """
    Function for grouping indicator questions by coded_cause. If coded_cause doesn't exists, it appends the question id
    to the 'unsorted' key
    :param indicator_question: question to be sorted
    :param coded_cause_dict: dict of existing coded_causes
    :return: dict with sorted questions by coded_cause
    """
    why_causes = indicator_question.why_causes.all()
    coded_causes = [why_cause.coded_causes.first() for why_cause in why_causes]

    for coded_cause in coded_causes:
        if coded_cause:
            coded_cause_dict[coded_cause.id].append(indicator_question.id)


def sort_question_by_coded_cause(coded_causes_dict):
    """
    Function for counting the number of coded_cause with the same id
    :param coded_causes_dict: dict with unsorted coded causes
    :return: list of dicts with sorted coded causes
    """

    coded_causes_response = list()

    for coded_cause in coded_causes_dict:
        temp_dict = dict()
        coded_cause_inst = CodedCause.objects.get(pk=coded_cause)
        coded_cause_serialized = CodedCauseSerializer(coded_cause_inst)
        temp_dict['coded_cause'] = coded_cause_serialized.data
        temp_dict['count'] = len(coded_causes_dict[coded_cause])
        coded_causes_response.append(temp_dict)
    return coded_causes_response


class CollectDataForIndicatorDashboard:
    def __init__(self, project, entity_id, indicator_type):
        self.project = project
        self.entity_id = entity_id
        self.entity = Entity.objects.filter(pk=entity_id).first()
        self.indicator_type = indicator_type
        self.questionnaire_list = self._get_questionnaire_list()

    def build_response(self):
        if self._questionnaires_has_indicator_question():
            return self._build_indicator_response()
        return self._build_default_response()

    def _build_indicator_response(self):
        indicator_details = self._get_indicator_details()
        return {
            'gauge': self._get_gauge(),
            'details': indicator_details['details'],
            'coded_causes': indicator_details['coded_causes'],
            'project_comment': self._get_project_comment()

        }

    @staticmethod
    def _build_default_response():
        return {
            'gauge': calculate_indicator_score([]),
            'details': [],
            'coded_causes': [],
            'project_comment': []
        }

    def _questionnaires_has_indicator_question(self):
        if self.questionnaire_list:
            return self.questionnaire_list.first().get_indicator_question(self.indicator_type) is not None
        else:
            return False

    def _get_gauge(self):
        indicator_list = get_indicator_scores(self.questionnaire_list, self.indicator_type)
        gauge = calculate_indicator_score(indicator_list)
        if self.entity:
            gauge['general_indicator'] = self._get_general_indicator()
        return gauge

    def _get_general_indicator(self):
        all_project_questionnaires = self._get_all_project_questionnaires()
        indicator_list = get_indicator_scores(all_project_questionnaires, self.indicator_type)
        return calculate_indicator_score(indicator_list)['indicator']

    def _get_project_comment(self):
        return get_indicator_project_comment(self.project, self.entity_id, self.indicator_type)

    def _get_indicator_details(self):
        return get_indicator_details(self.questionnaire_list, self.indicator_type)

    def _get_questionnaire_list(self):
        return Questionnaire.objects.get_project_questionnaires_for_entity(self.project, self.entity)

    def _get_all_project_questionnaires(self):
        return Questionnaire.objects.get_project_questionnaires(self.project)


def collect_data_for_overview_dashboard(project, entity_id):
    questionnaire_list = Questionnaire.objects.get_project_questionnaires_for_entity(project, entity_id)
    return calculate_overview_score(questionnaire_list, project, entity_id)


def get_project_indicator_questions_list(project):
    indicators = dict()
    indicators['indicator_list'] = set()
    try:
        # get the template questionnaire for this project
        template_questionnaire = project.research_methodology.questionnaires.first()
    except AttributeError:
        indicators['indicator_list'] = list()
        indicators['detail'] = 'No Research Methodology or template questionnaire defined for this project'
        return indicators
    for question in template_questionnaire.template_questions.all().order_by('-order'):
        if question.type == QuestionType.INDICATOR_QUESTION:
            indicators['indicator_list'].add(question.additional_info)
    return indicators


def get_company_indicator_questions_list(company):
    projects = company.projects.all()
    indicators = dict()
    indicators['indicator_list'] = set()
    for project in projects:
        try:
            template_questionnaire = project.research_methodology.questionnaires.first()
        except AttributeError:
            indicators['indicator_list'] = list()
            indicators['detail'] = '{} has either no Research Methodology or template questionnaire defined for this project'.format(project)
            return indicators
        for question in template_questionnaire.template_questions.all():
            if question.type == QuestionType.INDICATOR_QUESTION:
                indicators['indicator_list'].add(question.additional_info)
    return indicators


class CodedCausesPercentageTable:
    def __init__(self, indicator, project):
        self.indicator_questions = QuestionnaireQuestion.objects.get_project_specific_indicator_questions(project, indicator)

    def build_response(self):
        response = defaultdict(dict)
        coded_causes = self.extract_coded_causes_per_score()
        for score, coded_causes_info in coded_causes.items():
            number_of_questions = coded_causes_info.get('number_of_questions')
            for coded_cause, info in coded_causes_info['coded_causes'].items():
                response[score][coded_cause] = self.build_response_for_coded_cause(info, number_of_questions)
        return response

    def build_response_for_coded_cause(self, coded_cause_info, number_of_questions):
        number_of_why_causes = coded_cause_info.get('number_of_why_causes')
        questions = coded_cause_info.get('questions', [])
        return {
            "sentiment": coded_cause_info.get('sentiment'),
            "percentage": self.calculate_percentage(number_of_why_causes, number_of_questions),
            "departments": self.build_response_for_departments(questions, number_of_questions)
        }

    def build_response_for_departments(self, indicator_questions, number_of_questions):
        response = list()
        questions_by_departments = self.group_questions_by_department(indicator_questions)
        for department, questions in questions_by_departments.items():
            nr_of_why_causes = self.count_number_of_why_causes(questions)
            result = {
                "id": department.id,
                "name": department.name,
                "percentage": self.calculate_percentage(nr_of_why_causes, number_of_questions),
                "entities": self.build_response_for_entities(questions, number_of_questions)
            }
            response.append(result)
        return response

    def build_response_for_entities(self, indicator_questions, number_of_questions):
        response = list()
        questions_by_entities = self.group_questions_by_entity(indicator_questions)
        for entity, questions in questions_by_entities.items():
            nr_of_why_causes = self.count_number_of_why_causes(questions)
            result = {
                "id": entity.id,
                "name": entity.name,
                "percentage": self.calculate_percentage(nr_of_why_causes, number_of_questions),
                "sections": self.build_response_for_sections(questions, number_of_questions)
            }
            response.append(result)
        return response

    def build_response_for_sections(self, indicator_questions, number_of_questions):
        response = list()
        questions_by_section = self.group_questions_by_section(indicator_questions)
        for section, questions in questions_by_section.items():
            nr_of_why_causes = self.count_number_of_why_causes(questions)
            result = {
                "id": section.id,
                "name": section.name,
                "percentage": self.calculate_percentage(nr_of_why_causes, number_of_questions)
            }
            response.append(result)
        return response

    def extract_coded_causes_per_score(self):
        response = defaultdict(dict)
        grouped_why_causes_by_score = self.extract_why_cause_per_score()
        for score, why_causes_info in grouped_why_causes_by_score.items():
            response[score]['coded_causes'] = self.extract_coded_cause(why_causes_info['why_causes'])
            response[score]['number_of_questions'] = why_causes_info['number_of_questions']
        return response

    def extract_why_cause_per_score(self):
        response = defaultdict(dict)
        grouped_questions_by_score = self.group_questions_by_score()
        for score, questions_info in grouped_questions_by_score.items():
            response[score]['why_causes'] = self._extract_why_causes(questions_info['questions'])
            response[score]['number_of_questions'] = questions_info['number_of_questions']
            # response[score]['questions'] = questions_info['questions']
            # response[score]['number_of_why_causes'] = len(response[score]['why_causes'])
        return response

    def group_questions_by_score(self):
        response = defaultdict(dict)
        for score in range(1, 11):
            response[score]['questions'] = self.indicator_questions.filter(score=score)
            response[score]['number_of_questions'] = len(self.indicator_questions.filter(score=score))
        return response

    @staticmethod
    def group_questions_by_department(indicator_questions):
        result = dict()
        for indicator_question in indicator_questions:
            department = indicator_question.get_department()
            result.setdefault(department, []).append(indicator_question)
        return result

    @staticmethod
    def group_questions_by_entity(indicator_questions):
        result = dict()
        for indicator_question in indicator_questions:
            entity = indicator_question.get_entity()
            result.setdefault(entity, []).append(indicator_question)
        return result

    @staticmethod
    def group_questions_by_section(indicator_questions):
        result = dict()
        for indicator_question in indicator_questions:
            section = indicator_question.get_section()
            if section:
                result.setdefault(section, []).append(indicator_question)
        return result

    @staticmethod
    def calculate_percentage(number_of_why_causes, number_of_questions):
        return round(number_of_why_causes / number_of_questions * 100, 2)

    @staticmethod
    def extract_coded_cause(why_causes):
        response = defaultdict(lambda: defaultdict(list))
        for why_cause in why_causes:
            coded_cause = why_cause.coded_causes.first()
            if coded_cause:
                coded_cause_name = coded_cause.coded_label.name
                response[coded_cause_name]['why_causes'].append(why_cause)
                response[coded_cause_name]['number_of_why_causes'] = len(response[coded_cause_name]['why_causes'])
                response[coded_cause_name]['sentiment'] = coded_cause.sentiment
                response[coded_cause_name]['questions'].append(why_cause.question)
                # response[coded_cause_name]['number_of_questions'] = len(response[coded_cause_name]['questions'])
        return response

    @staticmethod
    def _extract_why_causes(questions):
        why_list = list()
        for question in questions:
            for why_cause in question.why_causes.all():
                why_list.append(why_cause)
        return why_list

    def count_number_of_why_causes(self, questions):
        return len(self._extract_why_causes(questions))
