from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_liter = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_PREPARING = 'preparing'
    STATUS_SERVED = 'served'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_SERVED, 'Served'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    VOLUME_CHOICES = [
        (Decimal('0.25'), '0.25L'),
        (Decimal('0.50'), '0.5L'),
        (Decimal('1.00'), '1L'),
        (Decimal('1.50'), '1.5L'),
        (Decimal('2.00'), '2L'),
    ]
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100, blank=True)
    volume = models.DecimalField(max_digits=3, decimal_places=2, choices=VOLUME_CHOICES)
    # Price copied from the menu at order time, so later menu changes don't affect old orders
    price_per_liter = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return (self.volume * self.price_per_liter).quantize(Decimal('0.01'))

    def __str__(self):
        return f"Order of {self.volume}L {self.menu_item.name} by {self.customer_name}"
