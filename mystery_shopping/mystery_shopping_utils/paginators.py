from rest_framework.pagination import PageNumberPagination


class EvaluationPagination(PageNumberPagination):

    page_size = 20


class DetractorRespondentPaginator(PageNumberPagination):

    page_size = 20


class ProjectStatisticsPaginator(PageNumberPagination):

    page_size = 20


class FrustrationWhyCausesPagination(PageNumberPagination):

    page_size = 20


class AppreciationWhyCausesPagination(PageNumberPagination):

    page_size = 20


class WhyCausesPagination(PageNumberPagination):

    page_size = 20
