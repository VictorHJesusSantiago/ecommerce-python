from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('success', True),
            ('pagination', OrderedDict([
                ('count', self.page.paginator.count),
                ('pages', self.page.paginator.num_pages),
                ('current_page', self.page.number),
                ('page_size', self.get_page_size(self.request)),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
            ])),
            ('results', data),
        ]))


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class LargeOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100


class CreatedAtCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'
    cursor_query_param = 'cursor'


class UpdatedAtCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-updated_at'
    cursor_query_param = 'cursor'


class ProductPagination(StandardResultsSetPagination):
    page_size = 24
    max_page_size = 100


class OrderPagination(StandardResultsSetPagination):
    page_size = 15


class ReviewPagination(SmallResultsSetPagination):
    page_size = 10


class SearchPagination(StandardResultsSetPagination):
    page_size = 20
    max_page_size = 50


class AdminPagination(StandardResultsSetPagination):
    page_size = 50
    max_page_size = 200
