from rest_framework import serializers
from .models import MenuItem, Order

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price_per_liter', 'available']

class OrderSerializer(serializers.ModelSerializer):

    menu_item = serializers.StringRelatedField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'menu_item', 'volume', 'customer_name', 'created_at', 'total_price']

    def get_total_price(self, obj):
        return round(obj.volume * float(obj.menu_item.price_per_liter), 2)

