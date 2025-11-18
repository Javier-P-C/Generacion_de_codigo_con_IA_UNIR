from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Product

Employee = get_user_model()


class ProductTests(TestCase):
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

    def test_create_product_as_manager(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Ibuprofen',
                'presentation': 'tablets',
                'substance': 'Ibuprofen 200mg',
                'price': '10.50',
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Ibuprofen')

    def test_create_product_as_assistant_fails(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Ibuprofen',
                'presentation': 'tablets',
                'substance': 'Ibuprofen 200mg',
                'price': '10.50',
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_list_products_as_authenticated(self):
        Product.objects.create(name='Paracetamol', presentation='tablets', substance='Paracetamol 500mg', price='5.00')
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
