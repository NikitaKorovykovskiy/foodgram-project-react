from rest_framework.pagination import PageNumberPagination

from foodgram.settings import LIMITRECIPE


class LimitPageNumberPagination(PageNumberPagination):
    page_size = LIMITRECIPE
    page_size_query_param = "limit"
