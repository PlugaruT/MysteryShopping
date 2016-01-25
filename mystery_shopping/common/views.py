from rest_framework import viewsets

from .models import Country
from .models import CountryRegion
from .models import County
from .models import City
from .models import Sector

from .serializer import CountrySerializer
from .serializer import CountryRegionSerializer
from .serializer import CountySerializer
from .serializer import CitySerializer
from .serializer import SectorSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    # todo: add permissions



class CountryRegionViewSet(viewsets.ModelViewSet):
    queryset = CountryRegion.objects.all()
    serializer_class = CountryRegionSerializer
    # todo: add permissions


class CountyViewSet(viewsets.ModelViewSet):
    queryset = County.objects.all()
    serializer_class = CountySerializer
    # todo: add permissions


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    # todo: add permissions


class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    # todo: add permissions
