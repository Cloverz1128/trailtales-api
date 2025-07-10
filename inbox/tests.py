from testing.testcases import TestCase
from inbox.services import NotificationService
from notifications.models import Notification  # 这是 notification库自己定义的 model


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.testuser1 = self.create_user('testuser1')
        self.testuser2 = self.create_user('testuser2')
        self.testuser1_tweet = self.create_tweet(self.testuser1)

    def test_send_comment_notification(self):
        # do not dispatch notification if tweet user == comment user
        comment = self.create_comment(self.testuser1, self.testuser1_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if tweet user != comment user
        comment = self.create_comment(self.testuser2, self.testuser1_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        # do not dispatch notification if tweet user == like user
        like = self.create_like(self.testuser1, self.testuser1_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if tweet user != like user
        like = self.create_comment(self.testuser2, self.testuser1_tweet)
        NotificationService.send_comment_notification(like)
        self.assertEqual(Notification.objects.count(), 1)