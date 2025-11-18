from django.contrib import admin

from .models import Sale, SaleDetail


class SaleDetailInline(admin.TabularInline):
    model = SaleDetail
    extra = 0
    readonly_fields = ('product', 'quantity', 'subtotal')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'date', 'total')
    list_filter = ('date', 'employee')
    search_fields = ('employee__username', 'employee__name')
    readonly_fields = ('date', 'total')
    inlines = [SaleDetailInline]
    ordering = ('-date',)


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'subtotal')
    list_filter = ('sale', 'product')
    search_fields = ('sale__id', 'product__name')
