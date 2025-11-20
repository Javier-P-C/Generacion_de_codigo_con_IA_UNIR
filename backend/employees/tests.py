"""
Unit tests for Employee model and API endpoints.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

Employee = get_user_model()


class EmployeeTests(TestCase):
    """Test employee creation, editing, deletion, and permissions."""

    def setUp(self):
        """Create test users with different roles."""
        self.client = APIClient()
        self.manager = Employee.objects.create_user(
            username='manager',
            password='manager123',
            name='Manager User',
            email='manager@test.com',
            role='MANAGER',
        )
        self.assistant = Employee.objects.create_user(
            username='assistant',
            password='assistant123',
            name='Assistant User',
            email='assistant@test.com',
            role='ASSISTANT',
        )

    def test_create_employee_as_manager(self):
        """Test that manager can create new employees."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/employees/',
            {
                'username': 'newuser',
                'password': 'pass123',
                'name': 'New User',
                'email': 'newuser@test.com',
                'role': 'ASSISTANT',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['role'], 'ASSISTANT')

    def test_create_manager_employee(self):
        """Test creating an employee with MANAGER role."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/employees/',
            {
                'username': 'newmanager',
                'password': 'pass123',
                'name': 'New Manager',
                'email': 'newmanager@test.com',
                'role': 'MANAGER',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'MANAGER')

    def test_create_employee_as_assistant_fails(self):
        """Test that assistant cannot create employees."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/employees/',
            {
                'username': 'newuser',
                'password': 'pass123',
                'name': 'New User',
                'email': 'newuser@test.com',
                'role': 'ASSISTANT',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_employees_as_authenticated(self):
        """Test that authenticated users can list employees."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_edit_employee_as_manager(self):
        """Test that manager can edit employee information."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.put(
            f'/api/employees/{self.assistant.id}/',
            {
                'username': 'assistant',
                'name': 'Updated Assistant Name',
                'email': 'updated@test.com',
                'role': 'ASSISTANT',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Assistant Name')
        self.assertEqual(response.data['email'], 'updated@test.com')

    def test_partial_edit_employee_as_manager(self):
        """Test that manager can partially update employee."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/employees/{self.assistant.id}/',
            {'name': 'Partially Updated Name'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Partially Updated Name')

    def test_edit_employee_as_assistant_fails(self):
        """Test that assistant cannot edit employees."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.put(
            f'/api/employees/{self.manager.id}/',
            {
                'username': 'manager',
                'name': 'Hacked Name',
                'email': 'hacked@test.com',
                'role': 'MANAGER',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_employee_as_manager(self):
        """Test that manager can delete employees."""
        # Create a new employee to delete
        new_employee = Employee.objects.create_user(
            username='todelete',
            password='pass123',
            name='To Delete',
            email='delete@test.com',
            role='ASSISTANT',
        )
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f'/api/employees/{new_employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify employee is deleted
        self.assertFalse(Employee.objects.filter(id=new_employee.id).exists())

    def test_delete_employee_as_assistant_fails(self):
        """Test that assistant cannot delete employees."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.delete(f'/api/employees/{self.manager.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_employee_detail(self):
        """Test retrieving employee details."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get(f'/api/employees/{self.manager.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'manager')
        self.assertEqual(response.data['role'], 'MANAGER')

    def test_unauthenticated_cannot_list_employees(self):
        """Test that unauthenticated users cannot list employees."""
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
