from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper


class NewsFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'), )
        unique_together = (('user', 'tweet'), )
        ordering = ('-created_at', )

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'
    
    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)