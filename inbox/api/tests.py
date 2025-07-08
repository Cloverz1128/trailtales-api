from notifications.models import Notification
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        self.testuser1, self.testuser1_client = self.create_user_and_client('testuser1')
        self.testuser2, self.testuser2_client = self.create_user_and_client('testuser2')
        self.testuser2_tweet = self.create_tweet(self.testuser2)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.testuser1_client.post(COMMENT_URL, {
            'tweet_id': self.testuser2_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.testuser1_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.testuser2_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)

class NotificationApiTests(TestCase):

    def setUp(self):
        self.testuser1, self.testuser1_client = self.create_user_and_client('testuser1')
        self.testuser2, self.testuser2_client = self.create_user_and_client('testuser2')
        self.testuser1_tweet = self.create_tweet(self.testuser1)

    def test_unread_count(self):
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.testuser1_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.testuser1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.testuser1, self.testuser1_tweet)
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.testuser1_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.testuser2_client.get(url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_mark_all_as_read(self):
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.testuser1_tweet.id,
        })
        comment = self.create_comment(self.testuser1, self.testuser1_tweet)
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.testuser1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.testuser1_client.get(mark_url)
        self.assertEqual(response.status_code, 405)

        # user2 can not mark user1's notifications
        response = self.testuser2_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

        response = self.testuser1_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.testuser1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.testuser1_tweet.id,
        })
        comment = self.create_comment(self.testuser1, self.testuser1_tweet)
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # anonymous can not access
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # testuser2 can't see notifications
        response = self.testuser2_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        # testuser1 can see notifications
        response = self.testuser1_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # after mark one
        notification = self.testuser1.notifications.first()
        notification.unread = False
        notification.save()
        response = self.testuser1_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.testuser1_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.testuser1_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)

    def test_update(self):
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.testuser1_tweet.id,
        })
        comment = self.create_comment(self.testuser1, self.testuser1_tweet)
        self.testuser2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        notification = self.testuser1.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        # require put
        response = self.testuser2_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)
        # notification can not be updated by others
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)
        
        response = self.testuser2_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)
        # updated to unread=False
        response = self.testuser1_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.testuser1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # 再标记为未读
        response = self.testuser1_client.put(url, {'unread': True})
        response = self.testuser1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)
        # 必须带 unread
        response = self.testuser1_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)
        # 不可修改其他的信息
        response = self.testuser1_client.put(url,
                                          {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'newverb')