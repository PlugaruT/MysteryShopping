from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    BooleanFilter,
    CharFilter,
    DateFromToRangeFilter,
    FilterSet,
    ModelMultipleChoiceFilter
)

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.mystery_shopping_utils.custom_filters import DetractorIndicatorMultipleChoiceFilter
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.users.models import ClientUser, DetractorRespondent, Shopper, User


class UserFilter(FilterSet):
    groups = AllValuesMultipleFilter(name="groups")

    class Meta:
        model = User
        fields = ['groups', ]


class ShopperFilter(FilterSet):
    license = BooleanFilter(name='has_drivers_license')
    sex = CharFilter(name='user__gender')
    age = DateFromToRangeFilter(name='user__date_of_birth')

    class Meta:
        model = Shopper
        fields = ['license', 'sex', 'age']


class ClientFilter(FilterSet):
    groups = AllValuesMultipleFilter(name="user__groups")

    class Meta:
        model = ClientUser
        fields = ['groups', 'company']


class DetractorFilter(FilterSet):
    places = ModelMultipleChoiceFilter(queryset=CompanyElement.objects.all(), name="evaluation__company_element")
    date = DateFromToRangeFilter(name="evaluation__time_accomplished", lookup_expr='date')
    questions = AllValuesMultipleFilter(name='number_of_questions')
    indicators = DetractorIndicatorMultipleChoiceFilter(name="evaluation__questionnaire__questions__additional_info",
                                                        conjoined=True, query_manager=Questionnaire.objects.filter)

    class Meta:
        model = DetractorRespondent
        fields = ['date', 'places', 'status', 'questions', 'indicators']
