from testing.testcases import TestCase
from rest_framework.test import APIClient
from tweets.models import Tweet, TweetPhoto
from django.core.files.uploadedfile import SimpleUploadedFile

TWEET_LIST_URL = '/api/tweets/'  # for GET
TWEET_CREATE_URL = '/api/tweets/'  # for POST
TWEET_RETRIEVE_API = '/api/tweets/{}/'

class TweetApiTests(TestCase):
    def setUp(self):

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
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # tweet with id= -1 does not exist, 
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        # can not get object in retrieve() and return 404
        self.assertEqual(response.status_code, 404)

        # get tweet with all comments 
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(user=self.user2, tweet=tweet, content="holly a comment")
        self.create_comment(self.user1, tweet, 'hmm...')
        # add more comments for other tweet
        self.create_comment(self.user1, self.create_tweet(self.user2), 'nothing')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)

    def test_create_with_files(self):
        # without tile
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'a selfie',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)
        
        # file list empty
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'a selfie',
            'files': [],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # single photo file
        # content require to be bytes, use str.encode convert it
        file = SimpleUploadedFile(
            name='selfie.jpg',
            content=str.encode('a fake image'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'a selfie',
            'files': [file],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        # multi photo files
        file1 = SimpleUploadedFile(
            name='selfie1.jpg',
            content=str.encode('selfie 1'),
            content_type='image/jpeg',
        )
        file2 = SimpleUploadedFile(
            name='selfie2.jpg',
            content=str.encode('selfie 2'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'two selfies',
            'files': [file1, file2],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 3)

        # api response including photo_urls
        retrieve_url = TWEET_RETRIEVE_API.format(response.data['id'])
        response = self.user1_client.get(retrieve_url)
        self.assertEqual(len(response.data['photo_urls']), 2)
        self.assertEqual('selfie1' in response.data['photo_urls'][0], True)
        self.assertEqual('selfie2' in response.data['photo_urls'][1], True)

        # max upload to 9
        files = [
            SimpleUploadedFile(
                name=f'selfie{i}.jpg',
                content=str.encode(f'selfie{i}'),
                content_type='image/jpeg',
            )
            for i in range(10)
        ]
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'failed due to number of photos exceeded limit',
            'files': files,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 3)

