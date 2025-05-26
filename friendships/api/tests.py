from testing.testcases import TestCase
from rest_framework.test import APIClient
from friendships.models import Friendship


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'

class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

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


    def test_follow(self):
        # follow require login
        url = FOLLOW_URL.format(self.testuser1.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # follow require get
        response = self.testuser2_client.get(url)
        self.assertEqual(response.status_code, 405) # method not allowed

        # can not follow yourself
        response = self.testuser1_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow success
        response = self.testuser2_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('created_at' in response.data, True)
        self.assertEqual('user' in response.data, True)
        self.assertEqual(response.data['user']['id'], self.testuser1.id)
        self.assertEqual(response.data['user']['username'], self.testuser1.username)
        # duplicate follow 400
        response = self.testuser2_client.post(url)
        self.assertEqual(response.status_code, 400)

        # follow with creating friendship
        count = Friendship.objects.count()
        response = self.testuser1_client.post(FOLLOW_URL.format(self.testuser2.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.testuser1.id)
        # require login to unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # require get to unfollow
        response = self.testuser2_client.get(url)
        self.assertEqual(response.status_code, 405)

        # can not follow yourself
        response = self.testuser1_client.post(url)
        self.assertEqual(response.status_code, 400)

        # unfollow success
        friendship = Friendship.objects.create(
            from_user=self.testuser2,
            to_user=self.testuser1,
        )
        count = Friendship.objects.count()
        response = self.testuser2_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # unfollow someone without following
        count = Friendship.objects.count()
        response = self.testuser2_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.testuser2.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # desc ordering
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        print(ts0)
        print(ts1)
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'testuser2_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'testuser2_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'testuser2_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.testuser2.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # desc ordering
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'testuser2_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'testuser2_follower0',
        )