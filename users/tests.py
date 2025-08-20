import logging
logger = logging.getLogger(__name__)

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .repository.repository import UserRepository
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/user/'
        self.login_url = '/api/user/auth/login/'
        self.logout_url = '/api/user/logout/'
        self.user_data = {
            'email': 'apitestuser@example.com',
            'username': 'apitestuser',
            'password': 'apipass123',
            'first_name': 'API',
            'last_name': 'Test',
            'role': 'user',
        }

    def test_register_api_success(self):
        logger.info('Testing successful registration...')
        response = self.client.post(self.register_url, self.user_data, format='json')
        logger.info(f'Register response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

    def test_register_api_duplicate(self):
        logger.info('Testing duplicate registration...')
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        logger.info(f'Duplicate register response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_login_api_success(self):
        logger.info('Testing successful login...')
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            'username': 'apitestuser',
            'password': 'apipass123',
        }, format='json')
        logger.info(f'Login response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('id', response.data)
        self.assertIn('user_id', response.data)

    def test_login_api_fail(self):
        logger.info('Testing failed login...')
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'wrongpass',
        }, format='json')
        logger.info(f'Failed login response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_logout_api_success(self):
        logger.info('Testing successful logout...')
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': 'apitestuser',
            'password': 'apipass123',
        }, format='json')
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(self.logout_url, {'refresh': refresh_token}, format='json')
        logger.info(f'Logout response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_logout_api_invalid_token(self):
        logger.info('Testing logout with invalid token...')
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': 'apitestuser',
            'password': 'apipass123',
        }, format='json')
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(self.logout_url, {'refresh': 'invalidtoken'}, format='json')
        logger.info(f'Logout with invalid token response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data)

    def test_get_users_list(self):
        logger.info('Testing get users list...')
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': 'apitestuser',
            'password': 'apipass123',
        }, format='json')
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.register_url)
        logger.info(f'Get users response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn('username', response.data[0])
        self.assertIn('user_id', response.data[0])
        self.assertIn('email', response.data[0])
        self.assertNotIn('id', response.data[0])
        self.assertNotIn('is_active', response.data[0])
        self.assertNotIn('is_staff', response.data[0])
        self.assertNotIn('is_superuser', response.data[0])

    def test_get_users_filter_by_username(self):
        logger.info('Testing get users filter by username...')
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': 'apitestuser',
            'password': 'apipass123',
        }, format='json')
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.register_url + '?user=apitestuser')
        logger.info(f'Get users filter by username response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(u['username'] == 'apitestuser' for u in response.data))

    def test_get_users_filter_by_user_id(self):
        logger.info('Testing get users filter by user_id...')
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': 'apitestuser',
            'password': 'apipass123',
        }, format='json')
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        users_response = self.client.get(self.register_url)
        user_id = users_response.data[0]['user_id']
        response = self.client.get(self.register_url + f'?user={user_id}')
        logger.info(f'Get users filter by user_id response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(u['user_id'] == user_id for u in response.data))

    def test_patch_user_email(self):
        logger.info('Testing patch user email...')
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': 'apitestuser',
            'password': 'apipass123',
        }, format='json')
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        users_response = self.client.get(self.register_url)
        user_id = users_response.data[0]['user_id']
        patch_url = f'/api/user/{user_id}/'
        patch_data = {'email': 'newemail@example.com'}
        response = self.client.patch(patch_url, patch_data, format='json')
        logger.info(f'Patch user email response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newemail@example.com')

    def test_password_reset_flow(self):
        logger.info('Testing password reset flow...')
        self.client.post(self.register_url, self.user_data, format='json')
        forgot_url = '/api/user/password-reset/forgot-password/'
        response = self.client.post(forgot_url, {'email': self.user_data['email']}, format='json')
        logger.info(f'Forgot password response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        user = User.objects.get(email=self.user_data['email'])
        otp = user.reset_otp
        self.assertIsNotNone(otp)
        verify_url = '/api/user/password-reset/verify-otp/'
        response = self.client.post(verify_url, {'email': self.user_data['email'], 'otp': otp}, format='json')
        logger.info(f'Verify OTP response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        reset_url = '/api/user/password-reset/reset-password/'
        new_password = 'newpass123'
        response = self.client.post(reset_url, {
            'email': self.user_data['email'],
            'otp': otp,
            'new_password': new_password
        }, format='json')
        logger.info(f'Reset password response: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        login_response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': new_password,
        }, format='json')
        logger.info(f'Login after password reset response: {login_response.data}')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
