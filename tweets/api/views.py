from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from tweets.models import Tweet
from tweets.api.serializers import TweetSerializer

class TweetViewSet(GenericViewSet):
    serializer_class = TweetSerializer

    def get_permissions(self):
        if self.action == 'list': 
            return [AllowAny(), ] 
        return [IsAuthenticated(), ]
    
    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response("Missing user_id", status=400)
        user_id=request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)

        return Response({"tweets": serializer.data,}) 

    def create(self, request):
        pass