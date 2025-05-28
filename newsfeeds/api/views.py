from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed


class NewsFeedViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(self.get_queryset(), many=True)
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)