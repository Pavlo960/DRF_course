from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MenuItem, Order
from .serializers import MenuItemSerializer, OrderSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# class MenuItemListView(generics.ListAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer


# class MenuItemDetailView(generics.RetrieveAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer


# class OrderListView(generics.ListAPIView):
#     serializer_class = OrderSerializer

#     def get_queryset(self):
#         queryset = Order.objects.all()
#         customer_name = self.request.query_params.get('customer_name')
#         if customer_name:
#             queryset = queryset.filter(customer_name__icontains=customer_name)
#         return queryset


# class OrderDetailView(generics.RetrieveAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filterset_fields = ['volume', 'customer_name']
    search_fields = ['customer_name', 'menu_item__name']
    ordering_fields = ['created_at', 'volume']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        my_orders = self.get_queryset().filter(owner=request.user)
        serializer = self.get_serializer(my_orders, many=True)
        return Response(serializer.data)