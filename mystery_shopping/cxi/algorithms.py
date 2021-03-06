from collections import defaultdict, namedtuple

from django.db.models import Count, Min
from django.db.models.query import Prefetch

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.cxi.models import CodedCause, ProjectComment, WhyCause
from mystery_shopping.cxi.serializers import CodedCauseSerializer, ProjectCommentSerializer
from mystery_shopping.mystery_shopping_utils.constants import ROUND_TO_DIGITS
from mystery_shopping.mystery_shopping_utils.utils import calculate_percentage, count_detractors, count_passives, \
    count_promoters, flatten_list_of_lists, remove_none_from_list
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.models import CustomWeight, Questionnaire, QuestionnaireQuestion, \
    QuestionnaireTemplateQuestion
from mystery_shopping.questionnaires.utils import first_or_none


def get_indicator_scores(questionnaire_list, indicator_type):
    """
    Returns a list of the indicator's marks

    :param questionnaire_list: list of questionnaires to get the indicator scores from
    :param indicator_type: can be anything
    :return: a list with the indicator's marks
    """
    questions = flatten_list_of_lists(map(lambda q: q.questions_list, questionnaire_list))
    filtered_questions = filter(lambda question: question.additional_info == indicator_type, questions)
    return [question.score for question in filtered_questions]


def mean(list_of_scores):
    """
    calculate the mean of a list
    :param list_of_scores: list of elements (numbers) to calculate the mean for
    :return: the arithmetic average
    """
    return float(sum(list_of_scores)) / max(len(list_of_scores), 1)


def use_mean_formula(marks, divide_by):
    average = mean(marks)
    result = (average - 1) / divide_by
    return round(result * 100, ROUND_TO_DIGITS)


def calculate_indicator_score_old_formula(indicator_marks):
    if not indicator_marks:
        return {
            'indicator': None,
            'promoters': None,
            'passives': None,
            'detractors': None
        }

    indicator_marks = remove_none_from_list(indicator_marks)

    detractors = count_detractors(indicator_marks)
    passives = count_passives(indicator_marks)
    promoters = count_promoters(indicator_marks)

    indicator_marks_length = len(indicator_marks)

    detractors_percentage = calculate_percentage(detractors, indicator_marks_length, round_to=0)
    passives_percentage = calculate_percentage(passives, indicator_marks_length, round_to=0)
    promoters_percentage = calculate_percentage(promoters, indicator_marks_length, round_to=0)
    indicator_score = promoters_percentage - detractors_percentage

    return {
        'indicator': round(indicator_score, ROUND_TO_DIGITS),
        'promoters': promoters_percentage,
        'passives': passives_percentage,
        'detractors': detractors_percentage
    }


def calculate_indicator_score_improved_formula(indicator_marks, divide_by):
    """

    :param indicator_marks: list of the indicator's scores
    :param divide_by: number used in the formula for arithmetic average
    :return:
    """
    score = {}

    divide_by = divide_by if divide_by is not 0 else 1
    if indicator_marks:
        score['indicator'] = use_mean_formula(indicator_marks, divide_by)
    else:
        score['indicator'] = None

    return score


def calculate_indicator_score(indicator_marks, new_algorithm=False, divide_by=10):
    """
    Calculates the detractors, promoters and passives scores for a given list of indicator scores

    :param indicator_marks: list of the indicator's scores
    :return: a dict with the 'indicator', 'promoters', 'detractors' and 'passives' keys, and scores respectively
    """
    if new_algorithm:
        return calculate_indicator_score_improved_formula(indicator_marks, divide_by)
    else:
        return calculate_indicator_score_old_formula(indicator_marks)


def sort_indicator_question_marks(indicator_dict, indicator_question, question):
    if question.type != QuestionType.INDICATOR_QUESTION and question.type == QuestionType.SINGLE_CHOICE:
        if question.answer_choices not in [None, []]:
            indicator_dict[question.additional_info][question.answer]['marks'].append(indicator_question.score)
        else:
            indicator_dict[question.additional_info]['other']['marks'].append(indicator_question.score)
            if question.answer is not None and question.answer.capitalize() not in \
                indicator_dict[question.additional_info]['other']['other_choices']:
                indicator_dict[question.additional_info]['other']['other_choices'].append(question.answer)


def group_questions_by_answer(questionnaire_list, indicator_type, indicator_details):
    """
    :param questionnaire_list: list of questionnaires from which to group the indicator scores by answer
    :param indicator_type: can be anything
    :return: the indicator's marks distributed per question choice selected
    :rtype: defaultdict
    """

    coded_causes_dict = defaultdict(list)

    for questionnaire in questionnaire_list:
        questionnaire_indicator_question = first_or_none([q for q in questionnaire.questions_list
                                                          if q.type == QuestionType.INDICATOR_QUESTION
                                                          and q.additional_info == indicator_type])

        if questionnaire_indicator_question:
            add_question_per_coded_cause(questionnaire_indicator_question, coded_causes_dict)

            for question in questionnaire.questions_list:
                sort_indicator_question_marks(indicator_details, questionnaire_indicator_question, question)

    return indicator_details, coded_causes_dict


def group_questions_by_pos(questionnaire_list, indicator_type):
    indicator_pos_details = defaultdict(lambda: defaultdict(list))
    for questionnaire in questionnaire_list:
        questionnaire_indicator_score = first_or_none([q for q in questionnaire.questions_list
                                                       if q.type == QuestionType.INDICATOR_QUESTION
                                                       and q.additional_info == indicator_type])
        if questionnaire_indicator_score:
            company_element = questionnaire.get_company_element()
            indicator_pos_details['entities'][company_element.element_name].append(
                questionnaire_indicator_score.score)
            indicator_pos_details['ids'][company_element.element_name] = company_element.id
    return indicator_pos_details


def create_details_skeleton(questionnaire_template):
    """
    Initialize structure of dict to contain all question choices

    :param questionnaire_template: Template Questionnaire to extract the choices from
    :return: initial structure of the indicator details
    """
    indicator_skeleton = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for question in questionnaire_template.template_questions.all().filter(type=QuestionType.SINGLE_CHOICE):
        for question_choice in question.template_question_choices.all():
            indicator_skeleton[question.additional_info][question_choice.text]['other_choices'] = []
            indicator_skeleton[question.additional_info][question_choice.text]['marks'] = []
            indicator_skeleton[question.additional_info][question_choice.text]['order'] = question_choice.order
    return indicator_skeleton


def get_respondents_distribution(list_of_marks):
    return {
        'detractors': count_detractors(list_of_marks),
        'passive': count_passives(list_of_marks),
        'promoters': count_promoters(list_of_marks)
    }


def sort_indicator_categories(details, indicator_categories, new_algorithm):
    for item_label, responses in indicator_categories.items():
        detail_item = dict()
        detail_item['results'] = list()
        for answer_choice in responses:
            answer_choice_result = dict()
            answer_choice_result['choice'] = answer_choice
            answer_choice_result['order'] = responses[answer_choice]['order']
            answer_choice_result['score'] = calculate_indicator_score(indicator_marks=responses[answer_choice]['marks'],
                                                                      new_algorithm=new_algorithm)
            answer_choice_result['distribution'] = get_respondents_distribution(responses[answer_choice]['marks'])
            answer_choice_result['number_of_respondents'] = len(responses[answer_choice]['marks'])
            answer_choice_result['other_answer_choices'] = responses[answer_choice]['other_choices']
            detail_item['results'].append(answer_choice_result)

        detail_item['item_label'] = item_label
        details.append(detail_item)
    return details


def sort_indicators_per_pos(details, indicators, new_algorithm):
    entity_key = 'entities'
    detail_item = defaultdict(list)
    detail_item['results'] = list()
    detail_item['item_label'] = entity_key.capitalize()
    for entity, marks in indicators.get(entity_key, {}).items():
        pos_detail = dict()
        pos_detail['choice'] = entity
        pos_detail['choice_id'] = indicators['ids'][entity]
        pos_detail['score'] = calculate_indicator_score(indicator_marks=marks, new_algorithm=new_algorithm)
        pos_detail['number_of_respondents'] = len(marks)
        pos_detail['other_answer_choices'] = indicators['ids'][entity]
        pos_detail['distribution'] = get_respondents_distribution(marks)
        detail_item['results'].append(pos_detail)
    details.append(detail_item)

    return details


def get_indicator_details(questionnaire_list, children_questionnaire_list, indicator_type, new_algorithm):
    """
    Collect detailed data about indicator_type

    :param questionnaire_list:
    :param indicator_type:
    :return: the indicator scores
    """
    details = list()
    template_questionnaire = questionnaire_list.first().template
    indicator_question = template_questionnaire.get_indicator_question(indicator_type)
    indicator_skeleton = create_details_skeleton(template_questionnaire)
    indicator_categories, coded_causes_dict = group_questions_by_answer(questionnaire_list, indicator_type,
                                                                        indicator_skeleton)
    sort_indicator_categories(details, indicator_categories, new_algorithm)

    if children_questionnaire_list.exists():
        indicators_per_pos = group_questions_by_pos(children_questionnaire_list, indicator_type)
        sort_indicators_per_pos(details, indicators_per_pos, new_algorithm)

    return_dict = dict()
    return_dict['details'] = details
    if indicator_question.allow_why_causes:
        coded_causes = sort_question_by_coded_cause(coded_causes_dict, questionnaire_list.count())
    else:
        coded_causes = []
    return_dict['coded_causes'] = coded_causes
    return return_dict


def get_overview_project_comment(project, company_element_id):
    project_comment = ProjectComment.objects.filter(project=project, company_element=company_element_id,
                                                    indicator="").first()
    return None if project_comment is None else ProjectCommentSerializer(project_comment).data


def get_indicator_project_comment(project, company_element_id, indicator_type):
    project_comment = ProjectComment.objects.filter(project=project, company_element=company_element_id,
                                                    indicator=indicator_type).first()
    return None if project_comment is None else ProjectCommentSerializer(project_comment).data


def calculate_weighed_value(value, weight):
    return float(value) * float(weight) / 100


def calculate_cxi_scores(return_dict, new_algorithm_indicator_dict, questionnaire_template):
    cxi_score = defaultdict(float)
    indicator_weights = CustomWeight.objects.extract_indicator_weights(questionnaire_template)
    for indicator_weight in indicator_weights:
        indicator = indicator_weight.get('question__additional_info')
        weight_name = indicator_weight.get('name')
        weight = indicator_weight.get('weight')

        new_algorithm_indicator = new_algorithm_indicator_dict.get(indicator, [])
        if new_algorithm_indicator:
            indicator_value = calculate_indicator_score(new_algorithm_indicator).get('indicator')
        else:
            indicator_value = return_dict[indicator]['indicator']

        cxi_score[weight_name] += calculate_weighed_value(indicator_value, weight)

    for weight in cxi_score:
        cxi_score[weight] = round(cxi_score[weight], ROUND_TO_DIGITS)
    return cxi_score


def get_indicator_types(indicator_set, questionnaire_list):
    return_dict = dict()
    indicators = dict()
    new_algorithm_indicator_dict = dict()

    for indicator in indicator_set:
        indicator_list = get_indicator_scores(questionnaire_list, indicator.type)
        indicators[indicator.type] = calculate_indicator_score(indicator_list, indicator.new_algorithm)
        if indicator.new_algorithm:
            new_algorithm_indicator_dict[indicator.type] = indicator_list

    return_dict['indicators'] = indicators

    try:
        questionnaire_template = questionnaire_list[0].template
    except IndexError:
        # if no questionnaires have been collected, just return the empty dict
        return return_dict
    return_dict['cxi_indicators'] = calculate_cxi_scores(indicators,
                                                         new_algorithm_indicator_dict,
                                                         questionnaire_template)
    return return_dict


def get_only_indicator_score(indicator_set, questionnaire_list):
    return_dict = dict()
    for indicator in indicator_set:
        indicator_list = get_indicator_scores(questionnaire_list, indicator.type)
        return_dict[indicator.type] = calculate_indicator_score(indicator_list, indicator.new_algorithm).get(
            'indicator')
    return return_dict


def get_indicator_questions(questionnaire_list):
    IndicatorType = namedtuple('IndicatorType', ['type', 'new_algorithm'])

    indicator_types_set = set()
    indicator_order = list()
    for questionnaire in questionnaire_list:
        indicator_questions = [q for q in questionnaire.questions_list if q.type == QuestionType.INDICATOR_QUESTION]
        for indicator_question in sorted(indicator_questions, key=lambda question: question.order):
            indicator_types_set.add(
                IndicatorType(indicator_question.additional_info, indicator_question.template_question.new_algorithm))
            if indicator_question.additional_info not in indicator_order:
                indicator_order.append(indicator_question.additional_info)
    return indicator_types_set, indicator_order


def calculate_overview_score(questionnaire_list, project, company_element_id):
    overview_list = dict()
    overview_list['indicator_order'] = list()
    indicator_types_set, overview_list['indicator_order'] = get_indicator_questions(questionnaire_list)
    overview_list['score'] = get_indicator_types(indicator_types_set, questionnaire_list)
    overview_list['project_comment'] = get_overview_project_comment(project, company_element_id)
    return overview_list


class GetPerDayQuestionnaireData:
    def __init__(self, start, end, company_id):
        self.questionnaire_list = Questionnaire.objects.get_questionnaires_for_company(company_id) \
            .filter(modified__range=[start, end]).order_by('modified')

    def build_response(self):
        response = list()
        grouped_questionnaires_by_date = self.group_questionnaires_by_date()
        for date, questionnaires in grouped_questionnaires_by_date.items():
            data = {
                'date': date,
                'general_indicators': self.calculate_indicators(questionnaires),
                'entities': self.build_result_for_entities(questionnaires),
                'sections': self.build_result_for_sections(questionnaires),
                'departments': self.build_result_for_departments(questionnaires)
            }
            response.append(data)
        return response

    def build_result_for_departments(self, questionnaire_list):
        result = dict()
        grouped_questionnaires_by_department = self.group_questionnaires_by_department(questionnaire_list)
        for entity, questionnaire in grouped_questionnaires_by_department.items():
            result[entity] = self.calculate_indicators(questionnaire)
        return result

    def build_result_for_entities(self, questionnaire_list):
        result = dict()
        grouped_questionnaires_by_entities = self.group_questionnaires_by_entity(questionnaire_list)
        for entity, questionnaire in grouped_questionnaires_by_entities.items():
            result[entity] = self.calculate_indicators(questionnaire)
        return result

    def build_result_for_sections(self, questionnaire_list):
        result = dict()
        grouped_questionnaires_by_sections = self.group_questionnaires_by_section(questionnaire_list)
        for section, questionnaire in grouped_questionnaires_by_sections.items():
            result[section] = self.calculate_indicators(questionnaire)
        return result

    def group_questionnaires_by_date(self):
        result = dict()
        for questionnaire in self.questionnaire_list:
            result.setdefault(str(questionnaire.modified.date()), []).append(questionnaire)
        return result

    @staticmethod
    def group_questionnaires_by_department(questionnaire_list):
        result = dict()
        for questionnaire in questionnaire_list:
            result.setdefault(questionnaire.get_department().name, []).append(questionnaire)
        return result

    @staticmethod
    def group_questionnaires_by_entity(questionnaire_list):
        result = dict()
        for questionnaire in questionnaire_list:
            result.setdefault(questionnaire.get_entity().name, []).append(questionnaire)
        return result

    @staticmethod
    def group_questionnaires_by_section(questionnaire_list):
        result = dict()
        for questionnaire in questionnaire_list:
            if questionnaire.get_section():
                result.setdefault(questionnaire.get_section().name, []).append(questionnaire)
        return result

    @staticmethod
    def calculate_indicators(questionnaire_list):
        result = dict()
        result['indicators'] = dict()
        indicator_types_set, _ = get_indicator_questions(questionnaire_list)
        result['indicators'] = get_only_indicator_score(indicator_types_set, questionnaire_list)
        result['indicators']['cxi'] = sum(result['indicators'].values()) / len(result['indicators'])
        result['number_of_questionnaires'] = len(questionnaire_list)
        return result


def add_question_per_coded_cause(indicator_question, coded_cause_dict):
    """
    Function for grouping indicator questions by coded_cause. If coded_cause doesn't exist, it appends the question id to the 'unsorted' key

    :param indicator_question: question to be sorted
    :param coded_cause_dict: dict of existing coded_causes
    :return: dict with sorted questions by coded_cause
    """
    why_causes = indicator_question.why_causes_list
    coded_causes = [first_or_none(why_cause.coded_causes_list) for why_cause in why_causes]

    for coded_cause in coded_causes:
        if coded_cause:
            coded_cause_dict[coded_cause.id].append(indicator_question.id)


def sort_question_by_coded_cause(coded_causes_dict, total_count):
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
        temp_dict['percentage'] = calculate_percentage(temp_dict['count'], total_count)
        coded_causes_response.append(temp_dict)
    return coded_causes_response


class CollectDataForIndicatorDashboard:
    def __init__(self, project, company_element_id, indicator_type, company_element_permissions):
        self.project = project
        self.company_element_id = company_element_id
        self.company_element = CompanyElement.objects.filter(pk=self.company_element_id).first()
        self.indicator_type = indicator_type
        self.new_algorithm = QuestionnaireTemplateQuestion.objects.use_new_algorithm(project, indicator_type)
        self.questionnaire_list = self._get_questionnaire_list()
        self.company_element_permissions = company_element_permissions
        self.children_questionnaire_list = self._get_children_questionnaire_list()

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
            return self.questionnaire_list[0].get_indicator_question(self.indicator_type) is not None
        else:
            return False

    def _get_gauge(self):
        indicator_list = get_indicator_scores(self.questionnaire_list, self.indicator_type)
        gauge = calculate_indicator_score(indicator_list, self.new_algorithm)
        if self.company_element:
            gauge['general_indicator'] = self._get_general_indicator()
        return gauge

    def _get_general_indicator(self):
        all_project_questionnaires = self._get_all_project_questionnaires()
        indicator_list = get_indicator_scores(all_project_questionnaires, self.indicator_type)
        return calculate_indicator_score(indicator_list, self.new_algorithm)['indicator']

    def _get_project_comment(self):
        return get_indicator_project_comment(self.project, self.company_element_id, self.indicator_type)

    def _get_indicator_details(self):
        return get_indicator_details(self.questionnaire_list, self.children_questionnaire_list,
                                     self.indicator_type, self.new_algorithm)

    def _prefetch_questions(self):
        coded_causes = Prefetch('coded_causes',
                                queryset=CodedCause.objects.all()
                                .only('coded_label__name', 'sentiment')
                                .select_related('coded_label'), to_attr='coded_causes_list')
        why_causes = Prefetch('why_causes',
                              queryset=WhyCause.objects.all()
                              .defer('answer')
                              .prefetch_related(coded_causes), to_attr='why_causes_list')
        return Prefetch('questions',
                        queryset=QuestionnaireQuestion.objects.all()
                        .defer('comment')
                        .select_related('template_question')
                        .prefetch_related(why_causes), to_attr='questions_list')

    def _get_questionnaire_list(self):
        questions = self._prefetch_questions()
        return (Questionnaire.objects
                .get_project_questionnaires_for_subdivision(project=self.project,
                                                            company_element=self.company_element)
                .select_related('template', 'evaluation', 'evaluation__company_element')
                .prefetch_related(questions))

    def _get_children_questionnaire_list(self):
        if self.company_element:
            questions = self._prefetch_questions()
            return (Questionnaire.objects
                    .get_project_questionnaires_for_subdivision_children(project=self.project,
                                                                         company_element=self.company_element)
                    .filter(evaluation__company_element_id__in=self.company_element_permissions)
                    .select_related('template', 'evaluation', 'evaluation__company_element')
                    .prefetch_related(questions))
        else:
            return self._filter_questionnaires_for_top_level_company_elements().filter(
                evaluation__company_element_id__in=self.company_element_permissions)

    def _get_top_level_of_company_elements(self):
        return self.questionnaire_list.aggregate(top_level=Min('evaluation__company_element__level')).get('top_level')

    def _filter_questionnaires_for_top_level_company_elements(self):
        top_level = self._get_top_level_of_company_elements()
        return self.questionnaire_list.filter(evaluation__company_element__level=top_level)

    def _get_all_project_questionnaires(self):
        questions = self._prefetch_questions()
        return (Questionnaire.objects
                .get_project_submitted_or_approved_questionnaires(self.project)
                .select_related('template', 'evaluation', 'evaluation__company_element')
                .prefetch_related(questions))


def collect_data_for_overview_dashboard(project, company_element_id):
    questions = Prefetch('questions',
                         queryset=QuestionnaireQuestion.objects.all()
                         .select_related('template_question'), to_attr='questions_list')
    questionnaire_list = (Questionnaire.objects
                          .select_related('template', 'evaluation')
                          .prefetch_related(questions))

    questionnaire_list = questionnaire_list.get_project_questionnaires_for_subdivision(project=project,
                                                                                       company_element=company_element_id).all()
    return calculate_overview_score(questionnaire_list, project, company_element_id)


def compute_cxi_score_per_company_element(project):
    questions = Prefetch('questions',
                         queryset=QuestionnaireQuestion.objects.all()
                         .select_related('template_question'), to_attr='questions_list')
    questionnaire_list = (Questionnaire.objects
                          .select_related('template', 'evaluation', 'evaluation__company_element')
                          .prefetch_related(questions))

    questionnaire_list = questionnaire_list.get_project_questionnaires_for_subdivision(project=project)
    grouped_questionnaires = group_questionnaires_per_company_element(questionnaire_list)
    result = dict()
    for company_element, questionnaires in grouped_questionnaires.items():
        result[company_element] = calculate_overview_score(questionnaires, project, None)['score']['cxi_indicators']
    return result


def group_questionnaires_per_company_element(questionnaire_list):
    result = dict()
    for questionnaire in questionnaire_list:
        company_element = questionnaire.get_company_element().element_name
        result.setdefault(company_element, []).append(questionnaire)
    return result


def get_project_indicator_questions_list(project):
    indicators = dict()
    indicators['indicator_list'] = set()
    indicators['indicators_with_why_causes'] = set()
    try:
        # get the template questionnaire for this project
        template_questionnaire = project.research_methodology.questionnaires.first()
    except AttributeError:
        indicators['indicator_list'] = list()
        indicators['detail'] = 'No Research Methodology or template questionnaire defined for this project'
        return indicators
    indicators['indicator_list'] = get_indicator_order(template_questionnaire)
    indicators['indicators_with_why_causes'] = get_indicators_with_why_causes(template_questionnaire)
    return indicators


def get_indicator_order(template_questionnaire):
    questions = template_questionnaire.template_questions.filter(type=QuestionType.INDICATOR_QUESTION).order_by(
        'order').values_list('additional_info', flat=True)
    return questions


def get_indicators_with_why_causes(template_questionnaire):
    indicators = template_questionnaire.template_questions.filter(type=QuestionType.INDICATOR_QUESTION,
                                                                  allow_why_causes=True).order_by(
        'order').values_list('additional_info', flat=True)
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
            indicators[
                'detail'] = '{} has either no Research Methodology or template questionnaire defined for this project'.format(
                project)
            return indicators
        for question in template_questionnaire.template_questions.all():
            if question.type == QuestionType.INDICATOR_QUESTION:
                indicators['indicator_list'].add(question.additional_info)
    return indicators


class CodedCausesPercentageTable:
    def __init__(self, indicator_questions):
        self.indicator_questions = indicator_questions

    def build_response(self):
        response = list()
        coded_causes = self.extract_coded_causes_per_score()
        for score, coded_causes_info in coded_causes.items():
            number_of_questions = coded_causes_info.get('number_of_questions')
            result = dict()
            result['score'] = score
            result['coded_causes'] = dict()
            for coded_cause, info in coded_causes_info['coded_causes'].items():
                result['coded_causes'][coded_cause] = self.build_response_for_coded_cause(info, number_of_questions)
            response.append(result)
        return response

    def build_response_for_coded_cause(self, coded_cause_info, number_of_questions):
        number_of_why_causes = coded_cause_info.get('number_of_why_causes')
        questions = coded_cause_info.get('questions', [])
        return {
            "sentiment": coded_cause_info.get('sentiment'),
            "percentage": calculate_percentage(number_of_why_causes, number_of_questions, ROUND_TO_DIGITS),
            "company_elements": self.build_response_for_company_elements(questions, number_of_questions)
        }

    def build_response_for_company_elements(self, indicator_questions, number_of_questions):
        response = list()
        questions_by_company_element = self.group_questions_by_company_element(indicator_questions)
        for company_element, questions in questions_by_company_element.items():
            nr_of_why_causes = len(questions)
            result = {
                "id": company_element.id,
                "name": company_element.element_name,
                "type": company_element.element_type,
                "percentage": calculate_percentage(nr_of_why_causes, number_of_questions, ROUND_TO_DIGITS),
                "company_elements": self.build_response_for_company_elements(questions, number_of_questions) if
                company_element.children.exists() else []
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
        return response

    def group_questions_by_score(self):
        response = defaultdict(dict)
        questions_scores = self.indicator_questions.values('score').annotate(number_of_questions=Count('score'))
        for item in questions_scores:
            score = item['score']
            response[score]['questions'] = self.indicator_questions.filter(score=score)
            response[score]['number_of_questions'] = item['number_of_questions']
        return response

    @staticmethod
    def group_questions_by_company_element(indicator_questions):
        result = dict()
        for indicator_question in indicator_questions:
            company_element = indicator_question.get_company_element()
            result.setdefault(company_element, []).append(indicator_question)
        return result

    @staticmethod
    def extract_coded_cause(why_causes):
        response = defaultdict(lambda: defaultdict(list))
        for why_cause in why_causes:
            coded_cause = first_or_none(why_cause.coded_causes.all())
            if coded_cause:
                coded_cause_name = coded_cause.coded_label.name
                response[coded_cause_name]['why_causes'].append(why_cause)
                response[coded_cause_name]['number_of_why_causes'] = len(response[coded_cause_name]['why_causes'])
                response[coded_cause_name]['sentiment'] = coded_cause.sentiment
                response[coded_cause_name]['questions'].append(why_cause.question)
        return response

    @staticmethod
    def _extract_why_causes(questions):
        why_list = list()
        for question in questions:
            for why_cause in question.why_causes.all():
                why_list.append(why_cause)
        return why_list
