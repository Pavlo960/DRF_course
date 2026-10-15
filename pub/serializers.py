from decimal import Decimal

from rest_framework import serializers

from .models import Category, MenuItem, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = MenuItem
        fields = [
            'id',
            'name',
            'category',
            'category_name',
            'description',
            'price_per_liter',
            'available',
        ]

    def validate_price_per_liter(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price per liter must be greater than zero')
        return value


class OrderSerializer(serializers.ModelSerializer):
    ALLOWED_VOLUMES = {value for value, _ in Order.VOLUME_CHOICES}

    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.filter(available=True)
    )
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')
    # Plain DecimalField so clients can send 0.5 or 1 instead of the exact choice keys
    volume = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'menu_item',
            'menu_item_name',
            'volume',
            'customer_name',
            'price_per_liter',
            'status',
            'created_at',
            'total_price',
        ]
        read_only_fields = ['id', 'price_per_liter', 'created_at']

    def validate_volume(self, value):
        if value not in self.ALLOWED_VOLUMES:
            allowed = ', '.join(label for _, label in Order.VOLUME_CHOICES)
            raise serializers.ValidationError(f'Volume must be one of: {allowed}')
        return value.quantize(Decimal('0.01'))

    def validate_status(self, value):
        request = self.context['request']
        if not request.user.is_staff:
            current = self.instance.status if self.instance else Order.STATUS_NEW
            if value != current:
                raise serializers.ValidationError('Only staff can change the order status.')
        return value

    def save(self, **kwargs):
        # Copy the current menu price whenever the menu item is set or changed
        menu_item = self.validated_data.get('menu_item')
        if menu_item and (self.instance is None or self.instance.menu_item_id != menu_item.id):
            kwargs['price_per_liter'] = menu_item.price_per_liter
        return super().save(**kwargs)
