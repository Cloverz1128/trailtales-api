from accounts.models import UserProfile
from testing.testcases import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
REGISTER_URL = '/api/accounts/register/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_URL = '/api/profiles/{}/'


class AccountApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.client = APIClient()
        self.user = self.create_user(
            username='testuser',
            email='testuser@email.com',
            password='correct password',
        )

    def test_login(self):
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 405)

        # wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        
        # correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['id'], self.user.id)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test get
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # test post
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_register(self):
        data = {
            'username': 'someone',
            'email': 'someone@email.com',
            'password': 'any password',
        }
        # test get
        response = self.client.get(REGISTER_URL, data)
        self.assertEqual(response.status_code, 405)

        # test invalid email
        response = self.client.post(REGISTER_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        
        self.assertEqual(response.status_code, 400)

        # password too short
        response = self.client.post(REGISTER_URL, {
            'username': 'someone',
            'email': 'someone@email.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        # username too log
        response = self.client.post(REGISTER_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@email.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # successful register
        response = self.client.post(REGISTER_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        # check user profile created
        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)
        
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

class UserProfileAPITests(TestCase):

    def test_update(self):
        testuser1, testuser1_client = self.create_user_and_client('testuser1')
        p = testuser1.profile
        p.nickname = 'old nickname'
        p.save()
        url = USER_PROFILE_DETAIL_URL.format(p.id)

        # anonymous user cannot update profile
        response = self.anonymous_client.put(url, {
            'nickname': 'a new nickname',
        })
        
        print(response)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

        # test can only be updated by user himself.
        _, testuser2_client = self.create_user_and_client('testuser2')
        response = testuser2_client.put(url, {
            'nickname': 'a new nickname',
        })
        # print(response.data)
        # ErrorDetail is a string
        # {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')
        p.refresh_from_db()
        self.assertEqual(p.nickname, 'old nickname')

        # update nickname
        response = testuser1_client.put(url, {
            'nickname': 'a new nickname',
        })
        self.assertEqual(response.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.nickname, 'a new nickname')

        # update avatar
        response = testuser1_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='my-avatar.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual('my-avatar' in response.data['avatar'], True)
        p.refresh_from_db()
        self.assertIsNotNone(p.avatar)
