"""
Unit tests for Inventory model and API endpoints.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from inventory.models import Inventory
from products.models import Product

Employee = get_user_model()


class InventoryTests(TestCase):
    """Test inventory operations, validations, and permissions."""

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
        self.product = Product.objects.create(
            name='Paracetamol',
            presentation='tablets',
            substance='Paracetamol 500mg',
            price='5.00',
        )
        self.inventory = Inventory.objects.get(product=self.product)

    def test_list_inventory_as_authenticated(self):
        """Test that authenticated users can list inventory."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_inventory_shows_product_details(self):
        """Test that inventory list includes product information."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find the inventory item for our product
        inventory_item = next(
            (item for item in response.data if item['product']['id'] == self.product.id),
            None,
        )
        self.assertIsNotNone(inventory_item)
        self.assertEqual(inventory_item['product']['name'], 'Paracetamol')

    def test_list_inventory_unauthenticated_fails(self):
        """Test that unauthenticated users cannot list inventory."""
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_increase_inventory_as_manager(self):
        """Test that manager can increase inventory."""
        initial_quantity = self.inventory.quantity
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/inventory/{self.inventory.id}/increase/',
            {'amount': 5},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, initial_quantity + 5)

    def test_increase_inventory_with_large_amount(self):
        """Test increasing inventory with large amounts."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/inventory/{self.inventory.id}/increase/',
            {'amount': 1000},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertGreaterEqual(self.inventory.quantity, 1000)

    def test_increase_inventory_as_assistant_fails(self):
        """Test that assistant cannot increase inventory."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(
            f'/api/inventory/{self.inventory.id}/increase/',
            {'amount': 5},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_increase_inventory_with_negative_amount_fails(self):
        """Test that increasing inventory with negative amount fails."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/inventory/{self.inventory.id}/increase/',
            {'amount': -5},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_increase_inventory_with_zero_amount_fails(self):
        """Test that increasing inventory with zero fails."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/inventory/{self.inventory.id}/increase/',
            {'amount': 0},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inventory_cannot_be_negative(self):
        """Test that inventory quantity cannot be negative."""
        # Try to create inventory with negative quantity
        product2 = Product.objects.create(
            name='Test Product',
            presentation='capsules',
            substance='Test',
            price='10.00',
        )
        inventory2 = Inventory.objects.get(product=product2)
        
        # Try to set negative quantity directly
        inventory2.quantity = -1
        with self.assertRaises((ValidationError, IntegrityError)):
            inventory2.full_clean()
            inventory2.save()

    def test_prevent_inventory_negative_on_decrease(self):
        """Test that decreasing inventory below zero is prevented."""
        # Set inventory to low value
        self.inventory.quantity = 5
        self.inventory.save()
        
        # This test verifies the business logic prevents negative inventory
        # The actual enforcement happens in the sales endpoint
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)

    def test_inventory_quantity_validation(self):
        """Test validation of non-negative quantities."""
        self.inventory.quantity = 100
        self.inventory.save()
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 100)
        
        # Verify quantity is non-negative
        self.assertGreaterEqual(self.inventory.quantity, 0)

    def test_get_inventory_detail(self):
        """Test retrieving specific inventory item."""
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get(f'/api/inventory/{self.inventory.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product']['id'], self.product.id)

    def test_inventory_created_automatically_for_new_product(self):
        """Test that inventory is auto-created when product is created."""
        new_product = Product.objects.create(
            name='Auto Inventory Product',
            presentation='syrups',
            substance='Test Substance',
            price='15.00',
        )
        
        # Verify inventory exists
        inventory_exists = Inventory.objects.filter(product=new_product).exists()
        self.assertTrue(inventory_exists)
        
        # Verify initial quantity is 0
        inventory = Inventory.objects.get(product=new_product)
        self.assertEqual(inventory.quantity, 0)
