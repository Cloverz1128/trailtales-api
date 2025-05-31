# from comments.api.permissions import IsObjectOwner
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer, 
    CommentSerializerForCreate,
)
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

class CommentViewSet(viewsets.GenericViewSet):
    """
    only implement list, create, update, destroy方法
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        # if self.action in ["destroy", 'update']:
        #     # attention the order, 先check authentication first, then check owner
        #     return [IsAuthenticated(), IsObjectOwner()]  # IsObjectOwner is self-defined permissions
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            "user_id": request.user.id,
            "tweet_id": request.data.get("tweet_id"),
            "content": request.data.get("content"),
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                "message": "Please check your input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        return Response(
            CommentSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )