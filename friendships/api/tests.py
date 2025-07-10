from testing.testcases import TestCase
from rest_framework.test import APIClient
from friendships.models import Friendship
from utils.paginations import FriendshipPagination


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'

class FriendshipApiTests(TestCase):

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
        self.assertEqual(len(response.data['results']), 3)
        # desc ordering
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'testuser2_following2',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'testuser2_following1',
        )
        self.assertEqual(
            response.data['results'][2]['user']['username'],
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
        self.assertEqual(len(response.data['results']), 2)
        # desc ordering
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'testuser2_follower1',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'testuser2_follower0',
        )
    
    def test_followers_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):  # generate followers
            follower = self.create_user('testuser1_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.testuser1)
            if follower.id % 2 == 0: 
                Friendship.objects.create(from_user=self.testuser2,
                                          to_user=follower)

        url = FOLLOWERS_URL.format(self.testuser1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # testuser2 has followed users with even id
        response = self.testuser2_client.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def test_followings_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):  # testuser1 follow all
            following = self.create_user('testuser1_following{}'.format(i))
            Friendship.objects.create(from_user=self.testuser1, to_user=following)
            if following.id % 2 == 0:  # testuser2 follow even ids
                Friendship.objects.create(from_user=self.testuser2,
                                          to_user=following)

        url = FOLLOWINGS_URL.format(self.testuser1.id) 
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # testuser2 has followed users with even id
        response = self.testuser2_client.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        # testuser1 has followed all his following users
        response = self.testuser1_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

    def _test_friendship_pagination(self, url, page_size, max_page_size):
        # get page1
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)
        # get page2
        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, 404)

        # test user can not customize page_size exceeds max_page_size
        response = self.anonymous_client.get(url, {'page': 1,
                                                   'size': max_page_size + 1})
        self.assertEqual(len(response.data['results']), max_page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        # test user can customize page size by param size
        response = self.anonymous_client.get(url, {'page': 1, 'size': 2}) #  default size=20, 2 pages, 40 items
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['total_pages'], page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)