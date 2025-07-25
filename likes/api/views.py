from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCreate,
    LikeSerializerForCancel,
)
from likes.models import Like
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from utils.decorators import required_params
from inbox.services import NotificationService


class LikeViewSet(GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializerForCreate
    permission_classes = [IsAuthenticated, ]

    @required_params(method='POST', params=['content_type', 'object_id'])
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance, created = serializer.get_or_create()
        if created:
            NotificationService.send_like_notification(instance)
        return Response(
            LikeSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    @required_params(method='POST', params=['content_type', 'object_id'])
    def cancel(self, request, *args, **kwargs):
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted = serializer.cancel()
        return Response({
            'success': True,
            'deleted': deleted,   # 可以知道是找到了再删除, 还是没有找到就删除了
        }, status=status.HTTP_200_OK)