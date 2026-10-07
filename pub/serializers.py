from rest_framework import serializers
from .models import MenuItem, Order


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price_per_liter', 'available']

    def validate_price_per_liter(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price per liter must be greater than zero')
        return value


class OrderSerializer(serializers.ModelSerializer):
    menu_item = serializers.StringRelatedField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'menu_item', 'volume', 'customer_name', 'created_at', 'total_price']

    def get_total_price(self, obj):
        return round(obj.volume * float(obj.menu_item.price_per_liter), 2)

    def validate(self, data):
        volume = data.get('volume')
        if volume and volume > 2.0:
            raise serializers.ValidationError('You can not order more than 2.0 liters at a time!')
        return data