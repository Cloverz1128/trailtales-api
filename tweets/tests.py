from datetime import timedelta
from testing.testcases import TestCase
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
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