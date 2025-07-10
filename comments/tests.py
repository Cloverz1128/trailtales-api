from testing.testcases import TestCase

class CommonModelTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.testuser1 = self.create_user('testuser1')
        self.tweet = self.create_tweet(self.testuser1)
        self.comment = self.create_comment(self.testuser1, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__, None)

    def test_like_set(self):
        self.create_like(self.testuser1, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.testuser1, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        testuser2 = self.create_user('testuser2')
        self.create_like(testuser2, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)