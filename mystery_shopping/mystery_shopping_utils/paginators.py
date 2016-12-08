from rest_framework.pagination import PageNumberPagination


class FrustrationWhyCausesPagination(PageNumberPagination):

    page_size = 20


class AppreciationWhyCausesPagination(PageNumberPagination):

    page_size = 20


class WhyCausesPagination(PageNumberPagination):

    page_size = 20
