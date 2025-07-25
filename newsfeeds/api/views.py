from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService


class NewsFeedViewSet(GenericViewSet):
    pagination_class = EndlessPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        # newsfeeds = NewsFeed.objects.filter(user=self.request.user)
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        if page is None:
            queryset = NewsFeed.objects.filter(user=request.user)
            page = self.paginate_queryset(queryset)
            
        serializer = NewsFeedSerializer(
            page, 
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)