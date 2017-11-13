from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    BooleanFilter,
    CharFilter,
    DateFromToRangeFilter,
    FilterSet
)

from mystery_shopping.users.models import ClientUser, Shopper, User


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
