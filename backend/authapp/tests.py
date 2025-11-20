"""
Unit tests for authentication endpoints (JWT token generation and refresh).
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

Employee = get_user_model()


class AuthenticationTests(TestCase):
    """Test JWT token generation, refresh, and role-based access."""

    def setUp(self):
        """Create test users with different roles."""
        self.client = APIClient()
        self.manager = Employee.objects.create_user(
            username='manager',
            password='manager123',
            name='Manager User',
            role='MANAGER',
        )
        self.assistant = Employee.objects.create_user(
            username='assistant',
            password='assistant123',
            name='Assistant User',
            role='ASSISTANT',
        )

    def test_login_generates_jwt_token(self):
        """Test that login endpoint returns access and refresh tokens."""
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'manager', 'password': 'manager123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])

    def test_login_with_invalid_credentials_fails(self):
        """Test that login fails with invalid credentials."""
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'manager', 'password': 'wrongpassword'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_returns_new_access_token(self):
        """Test that refresh endpoint returns a new access token."""
        # First, login to get tokens
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        refresh_token = login_response.data['refresh']
        
        # Use refresh token to get new access token
        response = self.client.post(
            '/api/auth/refresh/',
            {'refresh': refresh_token},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIsNotNone(response.data['access'])

    def test_refresh_with_invalid_token_fails(self):
        """Test that refresh fails with invalid token."""
        response = self.client.post(
            '/api/auth/refresh/',
            {'refresh': 'invalid-token-string'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_can_access_restricted_endpoints(self):
        """Test that manager can access manager-only endpoints."""
        # Login as manager
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'manager', 'password': 'manager123'},
            format='json',
        )
        access_token = login_response.data['access']
        
        # Try to create a product (manager-only operation)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Test Product',
                'presentation': 'tablets',
                'substance': 'Test Substance',
                'price': '10.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_assistant_cannot_access_manager_endpoints(self):
        """Test that assistant receives 403 error on manager-only endpoints."""
        # Login as assistant
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        access_token = login_response.data['access']
        
        # Try to create a product (manager-only operation)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Test Product',
                'presentation': 'tablets',
                'substance': 'Test Substance',
                'price': '10.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access_protected_endpoints(self):
        """Test that unauthenticated requests are rejected."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assistant_can_access_allowed_endpoints(self):
        """Test that assistant can access endpoints available to all authenticated users."""
        # Login as assistant
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        access_token = login_response.data['access']
        
        # Try to list products (allowed for all authenticated users)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
