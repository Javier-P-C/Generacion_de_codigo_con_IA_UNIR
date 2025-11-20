"""
Unit tests for Sales model and API endpoints.
"""
from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from inventory.models import Inventory
from products.models import Product
from sales.models import Sale, SaleDetail

Employee = get_user_model()


class SalesTests(TestCase):
    """Test sales operations, calculations, validations, and permissions."""

    def setUp(self):
        """Create test users, products, and inventory."""
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
            name='Paracetamol',
            presentation='tablets',
            substance='Paracetamol 500mg',
            price='5.00',
        )
        self.product2 = Product.objects.create(
            name='Ibuprofen',
            presentation='tablets',
            substance='Ibuprofen 200mg',
            price='10.00',
        )
        self.product3 = Product.objects.create(
            name='Aspirin',
            presentation='capsules',
            substance='Aspirin 100mg',
            price='7.50',
        )
        
        # Get auto-created inventory and set quantities
        self.inventory1 = Inventory.objects.get(product=self.product1)
        self.inventory1.quantity = 100
        self.inventory1.save()
        
        self.inventory2 = Inventory.objects.get(product=self.product2)
        self.inventory2.quantity = 50
        self.inventory2.save()
        
        self.inventory3 = Inventory.objects.get(product=self.product3)
        self.inventory3.quantity = 25
        self.inventory3.save()

    def test_create_sale_with_multiple_products(self):
        """Test creating a sale with multiple products."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 5},
                    {'product_id': self.product2.id, 'quantity': 2},
                    {'product_id': self.product3.id, 'quantity': 3},
                ]
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify sale was created
        sale_id = response.data['id']
        self.assertIsNotNone(sale_id)

    def test_sale_validates_stock_per_item(self):
        """Test that stock validation is done per item."""
        self.client.force_authenticate(user=self.assistant)
        
        # Try to sell more than available for one product
        response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 5},  # OK
                    {'product_id': self.product2.id, 'quantity': 100},  # Too much
                ]
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_subtotal_for_single_product(self):
        """Test subtotal calculation for a single product."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 3}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        sale_id = response.data['id']
        detail = SaleDetail.objects.get(sale_id=sale_id)
        
        # Subtotal = quantity * price = 3 * 5.00 = 15.00
        self.assertEqual(detail.subtotal, Decimal('15.00'))

    def test_calculate_total_for_multiple_products(self):
        """Test total calculation for multiple products."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 2},  # 2 * 5.00 = 10.00
                    {'product_id': self.product2.id, 'quantity': 3},  # 3 * 10.00 = 30.00
                    {'product_id': self.product3.id, 'quantity': 4},  # 4 * 7.50 = 30.00
                ]
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        sale_id = response.data['id']
        sale = Sale.objects.get(id=sale_id)
        
        # Total = 10.00 + 30.00 + 30.00 = 70.00
        self.assertEqual(sale.total, Decimal('70.00'))

    def test_sale_decrements_inventory_correctly(self):
        """Test that inventory is reduced correctly after sale."""
        initial_qty1 = self.inventory1.quantity
        initial_qty2 = self.inventory2.quantity
        
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.inventory1.refresh_from_db()
        self.inventory2.refresh_from_db()
        
        self.assertEqual(self.inventory1.quantity, initial_qty1 - 5)
        self.assertEqual(self.inventory2.quantity, initial_qty2 - 2)

    def test_sale_with_insufficient_stock_fails(self):
        """Test that sale fails when there's insufficient stock."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 200}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient stock', str(response.data))

    def test_employees_can_list_sales(self):
        """Test that employees can list all sales."""
        # Create a sale first
        self.client.force_authenticate(user=self.assistant)
        self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 2}]},
            format='json',
        )
        
        # List sales
        response = self.client.get('/api/sales/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_employees_can_view_sale_detail(self):
        """Test that employees can view sale details."""
        # Create a sale
        self.client.force_authenticate(user=self.assistant)
        create_response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 2}]},
            format='json',
        )
        sale_id = create_response.data['id']
        
        # View sale detail
        response = self.client.get(f'/api/sales/{sale_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], sale_id)

    def test_employees_can_view_sale_items(self):
        """Test that employees can view items in a sale."""
        # Create a sale with multiple items
        self.client.force_authenticate(user=self.assistant)
        create_response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 2},
                    {'product_id': self.product2.id, 'quantity': 1},
                ]
            },
            format='json',
        )
        sale_id = create_response.data['id']
        
        # View sale details endpoint
        response = self.client.get(f'/api/sales/{sale_id}/details/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_sale_creates_sale_details(self):
        """Test that sale automatically creates SaleDetail records."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 3}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        sale_id = response.data['id']
        details = SaleDetail.objects.filter(sale_id=sale_id)
        self.assertEqual(details.count(), 1)
        
        detail = details.first()
        self.assertEqual(detail.quantity, 3)
        self.assertEqual(detail.subtotal, Decimal('15.00'))
        self.assertEqual(detail.product_id, self.product1.id)

    def test_manager_can_create_sales(self):
        """Test that manager can also create sales."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 1}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_cannot_create_sales(self):
        """Test that unauthenticated users cannot create sales."""
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 1}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_list_sales(self):
        """Test that unauthenticated users cannot list sales."""
        response = self.client.get('/api/sales/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sale_with_zero_quantity_fails(self):
        """Test that sale with zero quantity is rejected."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 0}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sale_with_negative_quantity_fails(self):
        """Test that sale with negative quantity is rejected."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': -5}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sale_without_items_fails(self):
        """Test that sale without items is rejected."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/sales/',
            {'items': []},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
