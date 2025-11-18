from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

Employee = get_user_model()


class EmployeeTests(TestCase):
    def setUp(self):
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

    def test_create_employee_as_manager(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/employees/',
            {'username': 'newuser', 'password': 'pass123', 'name': 'New User', 'role': 'ASSISTANT'},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'newuser')

    def test_create_employee_as_assistant_fails(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/employees/',
            {'username': 'newuser', 'password': 'pass123', 'name': 'New User', 'role': 'ASSISTANT'},
        )
        self.assertEqual(response.status_code, 403)

    def test_list_employees_as_authenticated(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 2)
