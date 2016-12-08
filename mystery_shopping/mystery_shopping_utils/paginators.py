from rest_framework.pagination import PageNumberPagination


class EvaluationPagination(PageNumberPagination):

    page_size = 20


class DetractorRespondentPaginator(PageNumberPagination):

    page_size = 20


class ProjectStatisticsPaginator(PageNumberPagination):

    page_size = 20
