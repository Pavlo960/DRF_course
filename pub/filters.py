import django_filters

from .models import MenuItem, Order


class MenuItemFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='filter_category')

    class Meta:
        model = MenuItem
        fields = ['category', 'available']

    def filter_category(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(category_id=value)
        return queryset.filter(category__name__icontains=value)


class OrderFilter(django_filters.FilterSet):
    volume = django_filters.NumberFilter()
    customer_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['volume', 'customer_name', 'status']
