from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hours_to_now(self):
        test_user = User.objects.create_user(username='testuser')
        test_tweet = Tweet.objects.create(user=test_user, content="This is a test tweet!")
        test_tweet.created_at = utc_now() - timedelta(hours=10)
        self.assertEqual(test_tweet.hours_to_now, 10)