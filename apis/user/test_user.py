import unittest
from flask import Flask
from user import user
from auth.auth_service import AuthService
from config import TestingConfig
from unittest.mock import MagicMock


class UserBlueprintTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(user)
        self.app.config.from_object(TestingConfig)

        # Mock the AuthService here and set it in the config
        self.auth_service_mock = MagicMock(spec=AuthService)
        self.auth_service_mock.access_token_max_age = 600
        self.auth_service_mock.refresh_token_max_age = 86400
        self.app.config['AUTH_SERVICE'] = self.auth_service_mock

        self.client = self.app.test_client()

        # Enable Flask debugging, this will allow us to see the traceback of the error
        self.app.testing = True

    def test_login(self):
        self.auth_service_mock.authenticate.return_value = {
            'access_token': 'fake-access-token',
            'refresh_token': 'fake-refresh-token',
            'userinfo': {
                'username': 'testuser'
            }
        }

        # Now when the '/login' route calls the authenticate method, it will return the fake response
        response = self.client.post('/login',
                                    json={
                                        'username': 'testuser',
                                        'password': 'testuser'
                                    })

        print(response.data, 'response data')
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.auth_service_mock.logout.return_value = {
            'error': False,
            'message': 'Logout successful',
            'code': 200
        }

        response = self.client.post('/logout',
                                    json={'refresh_token': 'sometoken'})
        self.assertEqual(response.status_code, 200)

    def test_refresh(self):
        self.auth_service_mock.refresh.return_value = {
            'access_token': 'new-fake-token',
            'refresh_token': 'new-fake-refresh-token',
            'userinfo': {
                'username': 'testuser'
        # Add other userinfo attributes if needed
            }
        }

        response = self.client.post('/refresh',
                                    json={'refresh_token': 'sometoken'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('new-fake-token', response.json['data']['access_token'])

    def test_get_groups(self):
        self.auth_service_mock.get_roles_list.return_value = [
            'group1', 'group2'
        ]

        response = self.client.get('/groups')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data'], ['group1', 'group2'])

    def test_get_user_list(self):
        self.auth_service_mock.get_users.return_value = ['user1', 'user2']

        response = self.client.get('/user')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data'], ['user1', 'user2'])

    def test_add_user(self):
        self.auth_service_mock.create_user.return_value = {
            'username': 'newuser',
            'id': '123'
        }

        response = self.client.post('/user',
                                    json={
                                        'username': 'newuser',
                                        'password': 'password123'
                                    })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data']['username'], 'newuser')

    def test_update_user(self):
        self.auth_service_mock.update_user.return_value = {
            'username': 'updateduser',
            'id': '123'
        }

        response = self.client.put('/user/123',
                                   json={'username': 'updateduser'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data']['username'], 'updateduser')

    def test_delete_user(self):
        self.auth_service_mock.delete_user.return_value = '123'

        response = self.client.delete('/user/123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data'], '123')

    def test_get_user_info(self):
        self.auth_service_mock.get_user_info.return_value = {
            'username': 'existinguser',
            'id': '123'
        }

        response = self.client.get('/user/123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data']['username'], 'existinguser')


if __name__ == '__main__':
    unittest.main()
