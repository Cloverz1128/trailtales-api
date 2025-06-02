from rest_framework.test import APIClient
from testing.testcases import TestCase
from comments.models import Comment
from django.utils import timezone

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

    def test_update(self):
        comment = self.create_comment(self.testuser1, self.tweet, 'original')
        another_tweet = self.create_tweet(self.testuser2)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # put: anonymous can not update
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # not author can not update
        response = self.testuser2_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # can only update content
        before_updated_at = comment.updated_at # before change, save status first
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.testuser1_client.put(url, {
            'content': 'new',
            'user_id': self.testuser2.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })  # update to db
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db() 
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.testuser1)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)  #created_at can not be changed
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_destroy(self):
        comment = self.create_comment(
            user=self.testuser1,
            tweet=self.tweet
        )
        url = COMMENT_DETAIL_URL.format(comment.id)
        # anonymous user delete
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)
        # not author delete
        response = self.testuser2_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # author delete
        count = Comment.objects.count()
        response = self.testuser1_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)