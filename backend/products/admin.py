from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'presentation', 'substance', 'price')
    list_filter = ('presentation',)
    search_fields = ('name', 'substance')
    ordering = ('name',)
