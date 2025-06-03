from rest_framework.serializers import ModelSerializer, CharField
from accounts.api.serializers import UserSerializerForTweet
from tweets.models import Tweet
from comments.api.serializers import CommentSerializer

class TweetSerializer(ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')

class TweetSerializerForCreate(ModelSerializer):
    content = CharField(min_length=6, max_length=140)
    class Meta:
        model = Tweet
        # username from request.user, created_at and id will be auto created
        fields = ('content', )
    
    def create(self, validated_data):
        user = self.context['request'].user # get user from request
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
class TweetSerializerWithComments(TweetSerializer):
	comments = CommentSerializer(source='comment_set', many=True)
	class Meta:
		model = Tweet
		fields = ('id', 'user', 'created_at', 'content', 'comments')