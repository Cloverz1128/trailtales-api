from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'


class CommentApiTests(TestCase):
    def setUp(self):
        self.testuser1 = self.create_user('testuser1')
        self.testuser1_client = APIClient()
        self.testuser1_client.force_authenticate(self.testuser1)

        self.testuser2 = self.create_user('testuser2')
        self.testuser2_client = APIClient()
        self.testuser2_client.force_authenticate(self.testuser2)
        
        # user1 create tweet
        self.tweet = self.create_tweet(self.testuser1)

    def test_create(self):
        # anonymous_client can not create
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # without args can not create
        response = self.testuser1_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # only have tweet_id
        response = self.testuser1_client.post(
            COMMENT_URL,
            data={"tweet_id": self.tweet.id},
        )
        self.assertEqual(response.status_code, 400)

        # only have content
        response = self.testuser1_client.post(
            COMMENT_URL,
            data={"content": "ok"}
        )
        self.assertEqual(response.status_code, 400)

        # content too long
        response = self.testuser1_client.post(
            COMMENT_URL,
            data={
                "tweet_id": self.tweet.id,
                "content": "1"*141
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # with content and tweet_id
        response = self.testuser1_client.post(
            COMMENT_URL,
            data={
                "tweet_id": self.tweet.id,
                "content": "1",
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.testuser1.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], "1")
