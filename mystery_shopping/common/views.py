from rest_framework import viewsets

from .models import Country
from .serializer import CountrySerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    # todo: add permissions
