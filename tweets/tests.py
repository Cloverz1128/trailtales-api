from datetime import timedelta
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import TweetPhoto
from tweets.services import TweetService
from twitter.cache import USER_TWEETS_PATTERN
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.testuser1 = self.create_user(username='testuser1')
        self.tweet = self.create_tweet(user=self.testuser1, content="This is a test tweet!")

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)


    def test_like_set(self):
        self.create_like(self.testuser1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.testuser1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        testuser2 = self.create_user('testuser2')
        self.create_like(testuser2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.testuser1,
        )
        self.assertEqual(photo.user, self.testuser1)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)

        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)

    def test_cache_tweet_in_redis(self):
        tweet = self.create_tweet(self.testuser1)
        conn = RedisClient.get_connection()
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}', serialized_data)
        data = conn.get(f'tweet:not_exists')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)
        
class TweetServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.testuser1 = self.create_user('testuser1')

    def test_get_user_tweets(self):
        tweet_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.testuser1, 'tweet {}'.format(i))
            tweet_ids.append(tweet.id)
        tweet_ids = tweet_ids[::-1]

        RedisClient.clear()
        conn = RedisClient.get_connection()

        # cache miss
        tweets = TweetService.get_cached_tweets(self.testuser1.id)
        self.assertEqual([t.id for t in tweets], tweet_ids)

        # cache hit
        tweets = TweetService.get_cached_tweets(self.testuser1.id)
        self.assertEqual([t.id for t in tweets], tweet_ids)

        # cache updated
        new_tweet = self.create_tweet(self.testuser1, 'new tweet')
        tweets = TweetService.get_cached_tweets(self.testuser1.id)
        tweet_ids.insert(0, new_tweet.id)
        self.assertEqual([t.id for t in tweets], tweet_ids)

    def test_create_new_tweet_before_get_cached_tweets(self):
        tweet1 = self.create_tweet(self.testuser1, 'tweet1')

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_TWEETS_PATTERN.format(user_id=self.testuser1.id)
        self.assertEqual(conn.exists(key), False)
        tweet2 = self.create_tweet(self.testuser1, 'tweet2')
        self.assertEqual(conn.exists(key), True)

        tweets = TweetService.get_cached_tweets(self.testuser1.id)
        self.assertEqual([t.id for t in tweets], [tweet2.id, tweet1.id])