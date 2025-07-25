from django.test import TestCase as DjangoTestCase
from django.core.cache import caches
from friendships.models import Friendship
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from tweets.models import Tweet
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from newsfeeds.models import NewsFeed


class TestCase(DjangoTestCase):

    def clear_cache(self):
        caches['testing'].clear()

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client
    
    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'

        if email is None:
            email = f"{username}@email.com"
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
    
    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(
            user=user,
            content=content,
        )
    
    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(
            user=user,
            tweet=tweet,
            content=content,
        )
    
    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
        )
        return instance
    
    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)
    
    def create_friendship(self, from_user, to_user):
        return Friendship.objects.create(from_user=from_user, to_user=to_user)