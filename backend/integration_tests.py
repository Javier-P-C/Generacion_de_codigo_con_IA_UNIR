"""
Integration tests for the Pharmacy Management System backend.

These tests verify end-to-end workflows across multiple modules.
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


class AuthenticationIntegrationTests(TestCase):
    """Integration tests for authentication workflows."""

    def setUp(self):
        """Create test data."""
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

    def test_complete_login_flow(self):
        """Test complete login flow: send credentials, receive token, use token."""
        # 1. Login
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'manager', 'password': 'manager123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        # 2. Use access token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Refresh token to get new access token
        response = self.client.post(
            '/api/auth/refresh/',
            {'refresh': refresh_token},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_authenticated_user_can_access_application(self):
        """Test that authenticated user can access all allowed endpoints."""
        # Login
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Access various endpoints
        endpoints = [
            '/api/employees/',
            '/api/products/',
            '/api/inventory/',
            '/api/sales/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f'Failed to access {endpoint}',
            )

    def test_unauthenticated_user_cannot_access_application(self):
        """Test that unauthenticated user is blocked from protected endpoints."""
        endpoints = [
            '/api/employees/',
            '/api/products/',
            '/api/inventory/',
            '/api/sales/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f'Unauthenticated access allowed to {endpoint}',
            )

    def test_assistant_cannot_access_manager_routes(self):
        """Test that assistant is blocked from manager-only operations."""
        # Login as assistant
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Try manager-only operations
        # Create product
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Test',
                'presentation': 'tablets',
                'substance': 'Test',
                'price': '10.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Create employee
        response = self.client.post(
            '/api/employees/',
            {
                'username': 'test',
                'password': 'test123',
                'name': 'Test',
                'role': 'ASSISTANT',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EmployeeManagementIntegrationTests(TestCase):
    """Integration tests for employee management."""

    def setUp(self):
        """Create test data."""
        self.client = APIClient()
        self.manager = Employee.objects.create_user(
            username='manager',
            password='manager123',
            name='Manager User',
            role='MANAGER',
        )
        # Login as manager
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'manager', 'password': 'manager123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_create_employee_and_verify_in_list(self):
        """Test creating employee and verifying it appears in the list."""
        # Create employee
        response = self.client.post(
            '/api/employees/',
            {
                'username': 'newemployee',
                'password': 'pass123',
                'name': 'New Employee',
                'email': 'new@test.com',
                'role': 'ASSISTANT',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = response.data['id']
        
        # Verify in list
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        employee_ids = [emp['id'] for emp in response.data]
        self.assertIn(employee_id, employee_ids)

    def test_edit_employee_from_ui(self):
        """Test editing employee through API."""
        # Create employee
        create_response = self.client.post(
            '/api/employees/',
            {
                'username': 'toedit',
                'password': 'pass123',
                'name': 'To Edit',
                'email': 'edit@test.com',
                'role': 'ASSISTANT',
            },
            format='json',
        )
        employee_id = create_response.data['id']
        
        # Edit employee
        response = self.client.patch(
            f'/api/employees/{employee_id}/',
            {'name': 'Edited Name'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Edited Name')


class ProductManagementIntegrationTests(TestCase):
    """Integration tests for product management."""

    def setUp(self):
        """Create test data."""
        self.client = APIClient()
        self.manager = Employee.objects.create_user(
            username='manager',
            password='manager123',
            name='Manager User',
            role='MANAGER',
        )
        # Login as manager
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'manager', 'password': 'manager123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_create_product_and_verify_in_list(self):
        """Test creating product and checking it appears in the table."""
        # Create product
        response = self.client.post(
            '/api/products/',
            {
                'name': 'New Product',
                'presentation': 'tablets',
                'substance': 'Test Substance',
                'price': '15.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product_id = response.data['id']
        
        # Verify in list
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        product_ids = [prod['id'] for prod in response.data]
        self.assertIn(product_id, product_ids)

    def test_edit_product_from_ui(self):
        """Test editing product through API."""
        # Create product
        create_response = self.client.post(
            '/api/products/',
            {
                'name': 'To Edit',
                'presentation': 'tablets',
                'substance': 'Original',
                'price': '10.00',
            },
            format='json',
        )
        product_id = create_response.data['id']
        
        # Edit product
        response = self.client.patch(
            f'/api/products/{product_id}/',
            {'name': 'Edited Product', 'price': '12.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Edited Product')
        self.assertEqual(Decimal(response.data['price']), Decimal('12.00'))

    def test_delete_product_and_verify_removed(self):
        """Test deleting product and verifying it disappears from list."""
        # Create product
        create_response = self.client.post(
            '/api/products/',
            {
                'name': 'To Delete',
                'presentation': 'tablets',
                'substance': 'Test',
                'price': '10.00',
            },
            format='json',
        )
        product_id = create_response.data['id']
        
        # Delete product
        response = self.client.delete(f'/api/products/{product_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify not in list
        response = self.client.get('/api/products/')
        product_ids = [prod['id'] for prod in response.data]
        self.assertNotIn(product_id, product_ids)

    def test_create_product_with_invalid_data_shows_errors(self):
        """Test that creating product with invalid data returns backend errors."""
        # Try to create with invalid presentation
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Invalid',
                'presentation': 'invalid_type',
                'substance': 'Test',
                'price': '10.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('presentation', str(response.data).lower())


class InventoryManagementIntegrationTests(TestCase):
    """Integration tests for inventory management."""

    def setUp(self):
        """Create test data."""
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
        
        # Create product
        self.product = Product.objects.create(
            name='Test Product',
            presentation='tablets',
            substance='Test',
            price='10.00',
        )
        self.inventory = Inventory.objects.get(product=self.product)

    def test_show_complete_inventory_list_from_backend(self):
        """Test loading complete inventory list from backend."""
        # Login as assistant
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        
        # Get inventory list
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        
        # Verify structure
        for item in response.data:
            self.assertIn('id', item)
            self.assertIn('product', item)
            self.assertIn('quantity', item)

    def test_increase_inventory_as_manager_updates_ui(self):
        """Test increasing inventory as manager and verifying update."""
        # Login as manager
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'manager', 'password': 'manager123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        
        # Get initial quantity
        response = self.client.get(f'/api/inventory/{self.inventory.id}/')
        initial_qty = response.data['quantity']
        
        # Increase inventory
        response = self.client.post(
            f'/api/inventory/{self.inventory.id}/increase/',
            {'amount': 50},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify update
        response = self.client.get(f'/api/inventory/{self.inventory.id}/')
        self.assertEqual(response.data['quantity'], initial_qty + 50)

    def test_assistant_blocked_from_increasing_inventory(self):
        """Test that assistant cannot increase inventory."""
        # Login as assistant
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        
        # Try to increase inventory
        response = self.client.post(
            f'/api/inventory/{self.inventory.id}/increase/',
            {'amount': 50},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_sale_decreases_inventory_automatically(self):
        """Test that registering sale automatically reduces inventory."""
        # Set initial inventory
        self.inventory.quantity = 100
        self.inventory.save()
        
        # Login as assistant
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        
        # Register sale
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product.id, 'quantity': 10}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify inventory decreased
        response = self.client.get(f'/api/inventory/{self.inventory.id}/')
        self.assertEqual(response.data['quantity'], 90)


class SalesIntegrationTests(TestCase):
    """Integration tests for sales workflows."""

    def setUp(self):
        """Create test data."""
        self.client = APIClient()
        self.assistant = Employee.objects.create_user(
            username='assistant',
            password='assistant123',
            name='Assistant User',
            role='ASSISTANT',
        )
        
        # Create products
        self.product1 = Product.objects.create(
            name='Product 1',
            presentation='tablets',
            substance='Test 1',
            price='5.00',
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            presentation='capsules',
            substance='Test 2',
            price='10.00',
        )
        self.product3 = Product.objects.create(
            name='Product 3',
            presentation='syrups',
            substance='Test 3',
            price='15.00',
        )
        
        # Set inventory
        inv1 = Inventory.objects.get(product=self.product1)
        inv1.quantity = 100
        inv1.save()
        
        inv2 = Inventory.objects.get(product=self.product2)
        inv2.quantity = 50
        inv2.save()
        
        inv3 = Inventory.objects.get(product=self.product3)
        inv3.quantity = 25
        inv3.save()
        
        # Login
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'assistant', 'password': 'assistant123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_register_sale_with_multiple_products_from_ui(self):
        """Test registering a sale with multiple products."""
        response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 2},
                    {'product_id': self.product2.id, 'quantity': 3},
                    {'product_id': self.product3.id, 'quantity': 1},
                ]
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response contains sale data
        self.assertIn('id', response.data)
        self.assertIn('total', response.data)

    def test_backend_returns_correct_totals_and_subtotals(self):
        """Test that backend calculates and returns correct totals."""
        response = self.client.post(
            '/api/sales/',
            {
                'items': [
                    {'product_id': self.product1.id, 'quantity': 2},  # 2 * 5 = 10
                    {'product_id': self.product2.id, 'quantity': 3},  # 3 * 10 = 30
                ]
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        sale_id = response.data['id']
        
        # Get sale details
        response = self.client.get(f'/api/sales/{sale_id}/')
        total = Decimal(response.data['total'])
        self.assertEqual(total, Decimal('40.00'))

    def test_sell_more_than_available_shows_error_in_frontend(self):
        """Test that selling more than available shows error."""
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 200}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error message is present
        error_message = str(response.data)
        self.assertIn('stock', error_message.lower())

    def test_sales_list_loaded_correctly(self):
        """Test that sales list is loaded correctly."""
        # Create a sale
        self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 1}]},
            format='json',
        )
        
        # Get sales list
        response = self.client.get('/api/sales/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_insufficient_stock_returns_error_message(self):
        """Test that insufficient stock returns appropriate error message."""
        response = self.client.post(
            '/api/sales/',
            {'items': [{'product_id': self.product1.id, 'quantity': 1000}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check error message content
        self.assertIn('Insufficient stock', str(response.data))
