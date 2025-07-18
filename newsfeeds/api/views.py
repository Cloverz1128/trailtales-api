from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from utils.paginations import EndlessPagination


class NewsFeedViewSet(GenericViewSet):
    pagination_class = EndlessPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        newsfeeds = NewsFeed.objects.filter(user=self.request.user)
        newsfeeds = self.paginate_queryset(newsfeeds)
        serializer = NewsFeedSerializer(
            newsfeeds, 
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)