from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user_id=follower_id, tweet=tweet)
            for follower_id in FriendshipService.get_follower_ids(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet)) # add self
        NewsFeed.objects.bulk_create(newsfeeds)