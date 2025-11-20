"""
Unit tests for Product model and API endpoints.
"""
from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Product

Employee = get_user_model()


class ProductTests(TestCase):
    """Test product CRUD operations, validations, and permissions."""

    def setUp(self):
        """Create test users and initial products."""
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
        self.product = Product.objects.create(
            name='Paracetamol',
            presentation='tablets',
            substance='Paracetamol 500mg',
            price='5.00',
        )

    def test_list_products_as_authenticated(self):
        """Test that authenticated users can list products."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_products_unauthenticated_fails(self):
        """Test that unauthenticated users cannot list products."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_as_manager(self):
        """Test that manager can create new products."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Ibuprofen',
                'presentation': 'tablets',
                'substance': 'Ibuprofen 200mg',
                'price': '10.50',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Ibuprofen')
        self.assertEqual(response.data['presentation'], 'tablets')
        self.assertEqual(Decimal(response.data['price']), Decimal('10.50'))

    def test_create_product_with_valid_presentations(self):
        """Test creating products with all valid presentation types."""
        self.client.force_authenticate(user=self.manager)
        valid_presentations = ['tablets', 'capsules', 'syrups', 'suspensions', 'solutions', 'pills', 'injectables']
        
        for presentation in valid_presentations:
            response = self.client.post(
                '/api/products/',
                {
                    'name': f'Product {presentation}',
                    'presentation': presentation,
                    'substance': f'Substance for {presentation}',
                    'price': '15.00',
                },
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['presentation'], presentation)

    def test_create_product_with_invalid_presentation_fails(self):
        """Test that creating product with invalid presentation fails."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Invalid Product',
                'presentation': 'invalid_type',
                'substance': 'Test Substance',
                'price': '10.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_valid_decimal_price(self):
        """Test creating product with valid decimal price."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Decimal Product',
                'presentation': 'capsules',
                'substance': 'Test Substance',
                'price': '99.99',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data['price']), Decimal('99.99'))

    def test_create_product_with_negative_price_fails(self):
        """Test that creating product with negative price fails."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Negative Price Product',
                'presentation': 'tablets',
                'substance': 'Test Substance',
                'price': '-10.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_as_assistant_fails(self):
        """Test that assistant cannot create products."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Ibuprofen',
                'presentation': 'tablets',
                'substance': 'Ibuprofen 200mg',
                'price': '10.50',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_product_as_manager(self):
        """Test that manager can edit existing products."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.put(
            f'/api/products/{self.product.id}/',
            {
                'name': 'Updated Paracetamol',
                'presentation': 'capsules',
                'substance': 'Paracetamol 1000mg',
                'price': '7.50',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Paracetamol')
        self.assertEqual(response.data['presentation'], 'capsules')
        self.assertEqual(Decimal(response.data['price']), Decimal('7.50'))

    def test_partial_edit_product_as_manager(self):
        """Test that manager can partially update products."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/products/{self.product.id}/',
            {'price': '6.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['price']), Decimal('6.00'))
        self.assertEqual(response.data['name'], 'Paracetamol')

    def test_edit_product_as_assistant_fails(self):
        """Test that assistant cannot edit products."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.put(
            f'/api/products/{self.product.id}/',
            {
                'name': 'Hacked Product',
                'presentation': 'tablets',
                'substance': 'Hacked Substance',
                'price': '1.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_as_manager(self):
        """Test that manager can delete products."""
        # Create a product to delete
        product_to_delete = Product.objects.create(
            name='To Delete',
            presentation='syrups',
            substance='Delete Substance',
            price='20.00',
        )
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f'/api/products/{product_to_delete.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify product is deleted
        self.assertFalse(Product.objects.filter(id=product_to_delete.id).exists())

    def test_delete_product_as_assistant_fails(self):
        """Test that assistant cannot delete products."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_product_detail(self):
        """Test retrieving product details."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Paracetamol')
        self.assertEqual(response.data['presentation'], 'tablets')

    def test_create_product_without_required_fields_fails(self):
        """Test that creating product without required fields fails."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            '/api/products/',
            {'name': 'Incomplete Product'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
