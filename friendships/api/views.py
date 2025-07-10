
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerialierForCreate,
)
from friendships.api.paginations import FriendshipPagination

class FriendshipViewSet(GenericViewSet):
    serializer_class = FriendshipSerialierForCreate
    queryset = User.objects.all()
    pagination_class = FriendshipPagination
    
    # friendships/1/followers
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk): 
        friendships = Friendship.objects.filter(to_user=pk)
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user=pk)
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    # the rest api:
    # friendships/?from_user_id=1 to  get following list
    # friendships/?to_user_id=1 to get follower list
    def list(self, request):
        from_user_id = request.query_params.get('from_user_id')
        to_user_id = request.query_params.get('to_user_id')

        if to_user_id:
            followers = Friendship.objects.filter(to_user=to_user_id)
            serializer = FollowerSerializer(followers, many=True)
            return Response({
                'followers': serializer.data,
            }, status=status.HTTP_200_OK)
        
        elif from_user_id:
            followings = Friendship.objects.filter(from_user=from_user_id)
            serializer = FollowingSerializer(followings, many=True)
            return Response({
                'followings': serializer.data,
            }, status.HTTP_200_OK)

        else:
            return Response({
            'message': 'This is friendship homepage'
        })

    # friendships/<pk>/follow/
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        follow_user = self.get_object() # check if user with id=pk exist (from queryset)
        serializer = FriendshipSerialierForCreate(data={
                "from_user_id": request.user.id,
                "to_user_id": pk,
        })

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors":serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance, context={'request': request}).data, 
            status=status.HTTP_201_CREATED,
        )
    
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        unfollower_user = self.get_object() # raise 404， if no user id=pk
        if request.user.id == unfollower_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        
        return Response({'success': True, 'deleted': deleted})
