from testing.testcases import TestCase
from rest_framework.test import APIClient
from tweets.models import Tweet

TWEET_LIST_URL = '/api/tweets/'  # for GET
TWEET_CREATE_URL = '/api/tweets/'  # for POST


class TweetApiTests(TestCase):
    def setUp(self):
        
        self.anonymous_client = APIClient()

        self.user1 = self.create_user('user1')
        self.tweets1 = [self.create_tweet(
            user=self.user1,
        ) for i in range(3)]

        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1) # force_authenticate to use this authenticated user to do the access of all api

        self.user2 = self.create_user('user2')
        self.tweets2 = [self.create_tweet(
            user=self.user2,
        ) for i in range(2)]


    def test_list_api(self):
        # Test GET without user_id
        response = self.anonymous_client.get(TWEET_LIST_URL)
        self.assertEqual(response.status_code, 400)

        # Test GET with user_id in dictionary
        response = self.anonymous_client.get(
            path=TWEET_LIST_URL,
            data={'user_id': self.user1.id},
        )
        self.assertEqual(len(response.data['tweets']), 3)

        response = self.anonymous_client.get(
            path=TWEET_LIST_URL,
            data={'user_id': self.user2.id},
        )
        self.assertEqual(len(response.data['tweets']), 2)

        # Check order is DESC
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)


    def test_create_api(self):
        # test anonymous post tweet
        response = self.anonymous_client.post(TWEET_CREATE_URL, {'content': '1'})
        self.assertEqual(response.status_code, 403)

        # test post without content
        response = self.user1_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, 400)

        # validate tweet content 
        # content can not be too short
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': '1'})
        # print(response.status_code) 
        self.assertEqual(response.status_code, 400)
        # content can not be too long
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': '1'*141})
        self.assertEqual(response.status_code, 400)
        # test right case
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(
            TWEET_CREATE_URL,
            {'content': 'Hello this is my first tweet'}
        )
        self.assertEqual(response.status_code, 201)
        # print(response.data)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)