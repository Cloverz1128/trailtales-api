from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user_id=follower_id, tweet=tweet)
            for follower_id in FriendshipService.get_follower_ids(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet)) # add self
        NewsFeed.objects.bulk_create(newsfeeds)

        # as bulk create will not trigger post_save signal, need push to cache here
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)
    
    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by(
            '-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)