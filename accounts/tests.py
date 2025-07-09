from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_profile_property(self):
        testuser = self.create_user('testuser')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = testuser.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)