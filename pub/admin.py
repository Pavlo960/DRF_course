from django.contrib import admin

from .models import Category, MenuItem, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price_per_liter', 'available']
    list_filter = ['category', 'available']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'menu_item', 'volume', 'price_per_liter', 'status', 'customer_name', 'owner', 'created_at']
    list_filter = ['status']
    list_select_related = ['menu_item', 'owner']
