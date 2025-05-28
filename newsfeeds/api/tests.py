from rest_framework.test import APIClient

from testing.testcases import TestCase
from friendships.models import Friendship

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.testuser1 = self.create_user('testuser1')
        self.testuser1_client = APIClient()
        self.testuser1_client.force_authenticate(self.testuser1)

        self.testuser2 = self.create_user('testuser2')
        self.testuser2_client = APIClient()
        self.testuser2_client.force_authenticate(self.testuser2)

        # create followers and followings for testuser2
        for i in range(2):
            follower = self.create_user('testuser2_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.testuser2)

        for i in range(3):
            following = self.create_user('testuser2_following{}'.format(i))
            Friendship.objects.create(from_user=self.testuser2, to_user=following)

    def test_list(self):
        # require login
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)

        # can not use post
        response = self.testuser1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)

        # 0 newsfeed before post tweets
        response = self.testuser1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        # include author
        self.testuser1_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.testuser1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        # only followers can get tweets
        self.testuser1_client.post(FOLLOW_URL.format(self.testuser2.id))
        response = self.testuser1_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })

        posted_tweet_id = response.data['id']
        response = self.testuser1_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'],
                         posted_tweet_id)


