from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache() # before unittest clear cache
        self.testuser1 = self.create_user('testuser1')
        self.testuser2 = self.create_user('testuser2')

    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.testuser2]:
            Friendship.objects.create(from_user=self.testuser1, to_user=to_user)
        FriendshipService.invalidate_following_cache(self.testuser1.id)

        user_id_set = FriendshipService.get_following_user_id_set(self.testuser1.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.testuser2.id})

        Friendship.objects.filter(from_user=self.testuser1, to_user=self.testuser2).delete()
        FriendshipService.invalidate_following_cache(self.testuser1.id)
        user_id_set = FriendshipService.get_following_user_id_set(self.testuser1.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})