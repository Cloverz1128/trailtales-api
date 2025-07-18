from datetime import timedelta
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import TweetPhoto
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