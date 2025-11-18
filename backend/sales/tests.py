from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from inventory.models import Inventory
from products.models import Product
from sales.models import Sale, SaleDetail

Employee = get_user_model()


class SalesTests(TestCase):
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
        self.product1 = Product.objects.create(
            name='Paracetamol', presentation='tablets', substance='Paracetamol 500mg', price='5.00'
        )
        self.product2 = Product.objects.create(
            name='Ibuprofen', presentation='tablets', substance='Ibuprofen 200mg', price='10.00'
        )
        self.inventory1 = Inventory.objects.create(product=self.product1, quantity=100)
        self.inventory2 = Inventory.objects.create(product=self.product2, quantity=50)

    def test_create_sale_decrements_inventory(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 5},
                    {'product_id': self.product2.id, 'quantity': 2},
                ]
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.inventory1.refresh_from_db()
        self.inventory2.refresh_from_db()
        self.assertEqual(self.inventory1.quantity, 95)
        self.assertEqual(self.inventory2.quantity, 48)

    def test_sale_calculates_total_correctly(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 2},
                    {'product_id': self.product2.id, 'quantity': 3},
                ]
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        sale_id = response.data['id']
        sale = Sale.objects.get(id=sale_id)
        # 2 * 5.00 + 3 * 10.00 = 10 + 30 = 40
        self.assertEqual(sale.total, Decimal('40.00'))

    def test_sale_with_insufficient_stock_fails(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 200}]},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Insufficient stock', str(response.data))

    def test_sale_creates_sale_details(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 3}]},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        sale_id = response.data['id']
        details = SaleDetail.objects.filter(sale_id=sale_id)
        self.assertEqual(details.count(), 1)
        detail = details.first()
        self.assertEqual(detail.quantity, 3)
        self.assertEqual(detail.subtotal, Decimal('15.00'))

    def test_list_sales_as_authenticated(self):
        Sale.objects.create(employee=self.manager, total=100)
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/sales/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_sale_details_endpoint(self):
        sale = Sale.objects.create(employee=self.manager, total=Decimal('10.00'))
        SaleDetail.objects.create(sale=sale, product=self.product1, quantity=2, subtotal=Decimal('10.00'))
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get(f'/api/sales/{sale.id}/details/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
