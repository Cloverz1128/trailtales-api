from rest_framework.test import APIClient
from testing.testcases import TestCase
from comments.models import Comment
from django.utils import timezone

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'

class CommentApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.testuser1 = self.create_user('testuser1')
        self.testuser1_client = APIClient()
        self.testuser1_client.force_authenticate(self.testuser1)

        self.testuser2 = self.create_user('testuser2')
        self.testuser2_client = APIClient()
        self.testuser2_client.force_authenticate(self.testuser2)
        
        # user1 create tweet
        self.tweet = self.create_tweet(self.testuser1)

    def test_list(self):
        # require tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)
        #  has tweet_id, no comments
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)
        # comments in created_at order
        self.create_comment(self.testuser1, self.tweet, '1')
        self.create_comment(self.testuser2, self.tweet, '2')
        self.create_comment(self.testuser2, self.create_tweet(self.testuser2), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], "1")
        self.assertEqual(response.data['comments'][1]['content'], "2")

        # with user_id and tweet_id, only need tweet_id
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.testuser1.id,
        })
        self.assertEqual(len(response.data['comments']), 2)


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

    def test_comments_count(self):
        # test tweet detail api
        tweet = self.create_tweet(self.testuser1)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.testuser2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)  # create a tweet without comments

        # test tweet list api
        self.create_comment(self.testuser1, tweet)  # testuser1 add a comment
        response = self.testuser2_client.get(TWEET_LIST_API,
                                           {'user_id': self.testuser1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.testuser2, tweet)   # testuser2 add a comment
        self.create_newsfeed(self.testuser2, tweet)  # testuser2 subscribe a newsfeed
        response = self.testuser2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['results'][0]['tweet']['comments_count'], 
            2,
        )  # 2 comments

    
    def test_comments_count_with_cache(self):
        tweet_url = '/api/tweets/{}/'.format(self.tweet.id)
        response = self.testuser1_client.get(tweet_url)
        self.assertEqual(self.tweet.comments_count, 0)
        self.assertEqual(response.data['comments_count'], 0)

        data = {'tweet_id': self.tweet.id, 'content': 'a comment'}
        for i in range(2):
            _, client = self.create_user_and_client('user{}'.format(i))
            client.post(COMMENT_URL, data)
            response =client.get(tweet_url)
            self.assertEqual(response.data['comments_count'], i + 1)
            self.tweet.refresh_from_db()
            self.assertEqual(self.tweet.comments_count, i + 1)

        comment_data = self.testuser2_client.post(COMMENT_URL, data).data
        response = self.testuser2_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # update comment shouldn't update comments_count
        comment_url = '{}{}/'.format(COMMENT_URL, comment_data['id'])
        response = self.testuser2_client.put(comment_url, {'content': 'updated'})
        self.assertEqual(response.status_code, 200)
        response = self.testuser2_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # delete a comment will update comments_count
        response = self.testuser2_client.delete(comment_url)
        self.assertEqual(response.status_code, 200)
        response = self.testuser1_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 2)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 2)
