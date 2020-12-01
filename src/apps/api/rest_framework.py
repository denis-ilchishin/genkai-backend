from rest_framework import pagination


class Pagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
