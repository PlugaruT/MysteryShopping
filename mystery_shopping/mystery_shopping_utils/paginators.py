from rest_framework.pagination import PageNumberPagination


class EvaluationPagination(PageNumberPagination):

    page_size = 20
