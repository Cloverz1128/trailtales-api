from rest_framework.serializers import ModelSerializer
from accounts.api.serializers import UserSerializerForTweet
from tweets.models import Tweet

class TweetSerializer(ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
       
        model = Tweet

        fields = ('id', 'user', 'created_at', 'content')