from rest_framework.test import APIClient

from testing.testcases import TestCase
from friendships.models import Friendship
from utils.paginations import EndlessPagination

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
        self.assertEqual(len(response.data['results']), 0)

        # include author
        self.testuser1_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.testuser1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # only followers can get tweets
        self.testuser1_client.post(FOLLOW_URL.format(self.testuser2.id))
        response = self.testuser1_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })

        posted_tweet_id = response.data['id']
        response = self.testuser1_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'],
                         posted_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.testuser1, tweet=tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # pull the first page
        response = self.testuser1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'],
            newsfeeds[page_size - 1].id,
        )

        # pull the second page
        response = self.testuser1_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['id'], newsfeeds[page_size].id)
        self.assertEqual(results[1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(
            results[page_size - 1]['id'],
            newsfeeds[2 * page_size - 1].id,
        )

        # pull latest newsfeeds
        response = self.testuser1_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.testuser1, tweet=tweet)

        response = self.testuser1_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)