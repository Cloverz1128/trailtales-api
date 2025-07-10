from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class FriendshipPagination(PageNumberPagination):
    # https://.../api/friendships/1/followers/?page=3size=10
    page_size = 20 # default when urls don't have params
    page_size_query_param = 'size'
    
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })
    
    