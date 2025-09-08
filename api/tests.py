from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.db import connection
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import json

from api.models import User
from api.services import UserService
from api.utils import Result

class DockerTestDatabaseTestCase(TransactionTestCase):
    """Base class for database tests that use Dockerized PostgreSQL."""

    def setUp(self):
        super().setUp()
        self._clean_db()

    def tearDown(self):
        self._clean_db()
        super().tearDown()
    
    def _clean_db(self):
        """Clean the database by dropping all tables."""
        with connection.cursor() as cursor:
            cursor.execute("SET session_replication_role = 'replica';")

            cursor.execute("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename != 'django_migrations';
            """)

            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE;')
            
            cursor.execute("SET session_replication_role = 'origin';")


class UserAPITest(DockerTestDatabaseTestCase, APITestCase):
    """Test cases for the User API."""

    def setUp(self):
        self.client = APIClient()
        self.create_user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPassword123!"
        }
        self.login_user_data = {
            "email": "test@example.com",
            "password": "StrongPassword123!"
        }
    
    def test_create_user(self):
        """Test creating a new user."""

        url = reverse("account-create")
        response = self.client.post(url, self.create_user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["email"], self.create_user_data["email"])
        self.assertEqual(response.data["username"], self.create_user_data["username"])
        self.assertNotIn("password", response.data)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
    
    def test_login_user(self):
        """Test logging in a user."""

        url_create = reverse("account-create")
        create_response = self.client.post(url_create, self.create_user_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        url_login = reverse("login")

        # Wrong data test
        wrong_data = {
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }
        wrong_login_response = self.client.post(url_login, wrong_data, format="json")
        self.assertEqual(wrong_login_response.status_code, status.HTTP_400_BAD_REQUEST)

        # Correct data test
        correct_login_response = self.client.post(url_login, self.login_user_data, format="json")
        self.assertEqual(correct_login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", correct_login_response.data)
        self.assertIn("refresh_token", correct_login_response.data)
    
    def test_refresh_token(self):
        """Test refreshing a token."""
        
        url_create = reverse("account-create")
        create_response = self.client.post(url_create, self.create_user_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        url_login = reverse("login")
        login_response = self.client.post(url_login, self.login_user_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Extract tokens from response
        access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']

        # validate tokens
        self.assertIsInstance(access_token, str)
        self.assertIsInstance(refresh_token, str)
        self.assertGreater(len(access_token), 10)
        self.assertGreater(len(refresh_token), 10)

        # Test refreshing the token
        refresh_url = reverse("refresh-token")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        refresh_response = self.client.post(refresh_url, format="json", HTTP_X_REFRESH_TOKEN=refresh_token)
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

        # validate new tokens
        self.assertIn("access_token", refresh_response.data)
        self.assertIn("refresh_token", refresh_response.data)

        new_access_token = refresh_response.data["access_token"]
        new_refresh_token = refresh_response.data["refresh_token"]

        self.assertNotEqual(new_access_token, access_token)
        self.assertNotEqual(new_refresh_token, refresh_token)

        self.assertIsInstance(new_access_token, str)
        self.assertIsInstance(new_refresh_token, str)
        self.assertGreater(len(new_access_token), 10)
        self.assertGreater(len(new_refresh_token), 10)

        # Test that old refresh token is now blacklisted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        expired_refresh_response = self.client.post(refresh_url, format="json", HTTP_X_REFRESH_TOKEN=refresh_token)
        self.assertEqual(expired_refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test with empty refresh token
        empty_refresh_response = self.client.post(refresh_url, format="json", HTTP_X_REFRESH_TOKEN="")
        self.assertEqual(empty_refresh_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Test logging out a user."""
        
        url_create = reverse("account-create")
        create_response = self.client.post(url_create, self.create_user_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        url_login = reverse("login")
        login_response = self.client.post(url_login, self.login_user_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        logout_url = reverse("logout")

        logout_response = self.client.post(logout_url, format="json", HTTP_X_REFRESH_TOKEN=refresh_token)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # Test without accesstoken
        self.client.credentials()

        logout_response = self.client.post(logout_url, format="json", HTTP_X_REFRESH_TOKEN=refresh_token)
        self.assertEqual(logout_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test without refresh token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_response = self.client.post(logout_url, format="json", HTTP_X_REFRESH_TOKEN="")
        self.assertEqual(logout_response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_user(self):
        """Test updating a user."""

        url_create = reverse("account-create")
        create_response = self.client.post(url_create, self.create_user_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        url_login = reverse("login")
        login_response = self.client.post(url_login, self.login_user_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data['access_token']

        update_url = reverse("update-user")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        update_data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "StrongPassword123!?",
            "confirm_password": "StrongPassword123!?"
        }
        update_response = self.client.put(update_url, update_data, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Test without password
        update_data_without_password = {
            "username": "testuser3",
            "email": "test3@example.com",
        }
        update_response = self.client.put(update_url, update_data_without_password, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Test without confirm password
        update_data_without_confirm_password = {
            "username": "testuser4",
            "email": "test4@example.com",
            "password": "StrongPassword123!"
        }
        update_response = self.client.put(update_url, update_data_without_confirm_password, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with same data
        update_response = self.client.put(update_url, update_data_without_password, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Test with confirm password but without password
        update_data_with_confirm_password_without_password = {
            "username": "testuser5",
            "email": "test5@example.com",
            "confirm_password": "StrongPassword123!?"
        }
        update_response = self.client.put(update_url, update_data_with_confirm_password_without_password, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)