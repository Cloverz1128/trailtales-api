# from comments.api.permissions import IsObjectOwner
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer, 
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.api.permissions import IsObjectOwner
from rest_framework.response import Response
from utils.decorators import required_params

class CommentViewSet(viewsets.GenericViewSet):
    """
    only implement list, create, update, destroy方法
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        if self.action in ["destroy", 'update']:
            # attention the order, check authentication first, then check owner
            return [IsAuthenticated(), IsObjectOwner()]  # IsObjectOwner is self-defined permissions
        
        return [AllowAny()]
    
    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset() 
        comments = self.filter_queryset(queryset).prefetch_related('user').order_by('created_at')

        serializer = CommentSerializer(comments, many=True)
        return Response({
            'comments': serializer.data,
        }, status=status.HTTP_200_OK)

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
    
    def update(self, request, *args, **kwargs):
        # if serializer has instance, then when call save() it will call update() in serializer, otherwise call create()
        comment = self.get_object() 
        serializer = CommentSerializerForUpdate(
            instance=comment, 
            data=request.data, 
        )
        if not serializer.is_valid():
            return Response({
                'message': "Please check input",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data, 
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs): # have to add *args here, otherwise can not pass pk
        comment = self.get_object()
        comment.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)