
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
)

class FriendshipViewSet(GenericViewSet):
    
    queryset = User.objects.all()
    
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk): 
        friendships = Friendship.objects.filter(to_user=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({
            'followers': serializer.data,
        }, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user=pk)
        serializer = FollowingSerializer(friendships, many=True)
        return Response({
            'followings': serializer.data,
        }, status.HTTP_200_OK)

    # the rest api:
    # friendships/?from_user_id=1 to  get following list
    # friendships/?to_user_id=1 to get follower list
    def list(self, request):
        print(request.query_params)
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