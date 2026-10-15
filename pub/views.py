from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import MenuItemFilter, OrderFilter
from .models import Category, MenuItem, Order
from .permissions import IsAdminOrReadOnly, IsEditableByCustomer, IsOwnerOrStaff
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category')
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_class = MenuItemFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price_per_liter']
    ordering = ['id']


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff, IsEditableByCustomer]

    filterset_class = OrderFilter
    search_fields = ['customer_name', 'menu_item__name']
    ordering_fields = ['created_at', 'volume']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Order.objects.select_related('menu_item', 'owner')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        customer_name = (
            serializer.validated_data.get('customer_name')
            or user.get_full_name()
            or user.username
        )
        serializer.save(owner=user, customer_name=customer_name)

    @action(detail=False, methods=['get'])
    def my(self, request):
        my_orders = self.filter_queryset(self.get_queryset().filter(owner=request.user))
        serializer = self.get_serializer(my_orders, many=True)
        return Response(serializer.data)
