from rest_framework.filters import FilterSet

from mystery_shopping.common.models import Tag


class TagFilter(FilterSet):
    class Meta:
        model = Tag
        fields = ['type']
