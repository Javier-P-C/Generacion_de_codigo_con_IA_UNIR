from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from inventory.models import Inventory
from products.models import Product

Employee = get_user_model()


class InventoryTests(TestCase):
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
        self.product = Product.objects.create(
            name='Paracetamol', presentation='tablets', substance='Paracetamol 500mg', price='5.00'
        )
        self.inventory = Inventory.objects.create(product=self.product, quantity=10)

    def test_list_inventory_as_authenticated(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_increase_inventory_as_manager(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(f'/api/inventory/{self.inventory.id}/increase/', {'amount': 5})
        self.assertEqual(response.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 15)

    def test_increase_inventory_as_assistant_fails(self):
        self.client.force_authenticate(user=self.assistant)
        response = self.client.post(f'/api/inventory/{self.inventory.id}/increase/', {'amount': 5})
        self.assertEqual(response.status_code, 403)

    def test_inventory_cannot_go_negative(self):
        """Test that inventory quantity constraint is enforced."""
        from django.core.exceptions import ValidationError
        from django.db.utils import IntegrityError

        inv = Inventory(product=self.product, quantity=-1)
        # Either ValidationError or IntegrityError can occur depending on constraint enforcement
        with self.assertRaises((ValidationError, IntegrityError)):
            inv.full_clean()
            inv.save()
