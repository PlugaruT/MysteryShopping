from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mystery_shopping.common.filters import TagFilter
from mystery_shopping.common.models import City, Country, CountryRegion, County, Sector, Tag
from mystery_shopping.common.serializer import CitySerializer, CountryRegionSerializer, CountrySerializer, \
    CountySerializer, SectorSerializer, TagSerializer
from mystery_shopping.common.uploads import handle_csv_with_uploaded_countries, handle_csv_with_uploaded_localities


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = TagFilter
    permission_classes = (IsAuthenticated,)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAuthenticated,)


class CountryRegionViewSet(viewsets.ModelViewSet):
    queryset = CountryRegion.objects.all()
    serializer_class = CountryRegionSerializer
    permission_classes = (IsAuthenticated,)


class CountyViewSet(viewsets.ModelViewSet):
    queryset = County.objects.all()
    serializer_class = CountySerializer
    permission_classes = (IsAuthenticated,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super(CityViewSet, self).get_queryset()
        query_variable = self.request.query_params.get('q', None)

        # Search city by name
        if query_variable is not None:
            queryset = queryset.filter(name__icontains=query_variable)

        return queryset


class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = (IsAuthenticated,)


class LocalityCsvUploadView(APIView):
    """
        A view for uploading a .csv with all the localities to the platform.
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, *args, **kwargs):
        csv_file = request.data.get('file', None)
        if csv_file.content_type == 'text/csv':
            handle_csv_with_uploaded_localities(csv_file)
            return Response({
                'message': 'File uploaded successfully!'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'details': 'File type is not .csv'
            }, status=status.HTTP_400_BAD_REQUEST)


class CountryCsvUploadView(APIView):
    """
        A view for uploading a .csv with all the countries to the platform.
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, *args, **kwargs):
        csv_file = request.data.get('file', None)
        if csv_file.content_type == 'text/csv':
            handle_csv_with_uploaded_countries(csv_file)
            return Response({
                'message': 'File uploaded successfully!'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'details': 'File type is not .csv'
            }, status=status.HTTP_400_BAD_REQUEST)
