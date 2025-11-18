from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

Employee = get_user_model()


class Command(BaseCommand):
    help = 'Create a default superuser if none exists'

    def handle(self, *args, **options):
        if not Employee.objects.filter(is_superuser=True).exists():
            username = 'admin'
            password = 'admin123'
            Employee.objects.create_superuser(
                username=username,
                password=password,
                email='admin@example.com',
                name='Admin User',
                role='MANAGER',
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))
