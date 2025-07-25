from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from accounts.api.serializers import UserSerializerForTweet
from tweets.constants import TWEET_PHOTOS_UPLOAD_LIMIT
from tweets.models import Tweet
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService
from tweets.services import TweetService
from utils.redis_helper import RedisHelper

class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet(source='cached_user')
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    photo_urls = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
             'id', 
             'user', 
             'created_at', 
             'content',
             'comments_count',
             'likes_count',
             'has_liked',
             'photo_urls',
             )
    def get_comments_count(self, obj):
        # optimize: select count(*) -> redis get
        return RedisHelper.get_count(obj, 'comments_count')
    
    def get_likes_count(self, obj):
        # optimize: select count(*) -> redis get
        return RedisHelper.get_count(obj, 'likes_count')

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)
    
    def get_photo_urls(self, obj):
        photo_urls = []
        for photo in obj.tweetphoto_set.all().order_by('order'):
            photo_urls.append(photo.file.url)
        return photo_urls
    
class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,  # check value is []
        required=False,  # check the key 'files'
    )

    class Meta:
        model = Tweet
        # username from request.user, created_at and id will be auto created
        fields = ('content', 'files',)

    def validate(self, data):
        if len(data.get('files', [])) > TWEET_PHOTOS_UPLOAD_LIMIT:
            raise ValidationError({
                'message': f'You can upload {TWEET_PHOTOS_UPLOAD_LIMIT} photos '
                           'at most'
            })
        return data
    
    def create(self, validated_data):

        user = self.context['request'].user # get user from request
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)

        # create tweet first then link the photos
        if validated_data.get('files'):
            TweetService.create_photos_from_files(
                tweet=tweet,
                files=validated_data['files'],
            )
        return tweet
    
class TweetSerializerForDetail(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)
    class Meta:
        model = Tweet
        fields = (
            'id', 
            'user', 
            'created_at',
            'content',
            'comments',
            'likes',
            'likes_count',
            'comments_count',
            'has_liked',
            'photo_urls',
        )