from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

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
    VOLUME_CHOICES = [
        (0.25, '0.25L'),
        (0.5, '0.5L'),
        (1.0, '1L'),
        (1.5, '1.5L'),
        (2.0, '2L'),
    ]
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100)
    volume = models.FloatField(choices=VOLUME_CHOICES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order of {self.volume}L {self.menu_item.name} by {self.customer_name}"