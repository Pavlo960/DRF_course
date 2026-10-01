from django.urls import path
from . import views

urlpatterns = [
    path('api/menu/', views.MenuItemListView.as_view(), name='api_menu_list'),
    path('api/menu/<int:pk>/', views.MenuItemDetailView.as_view(), name='api_menu_detail'),
    
    path('api/orders/', views.OrderListView.as_view(), name='api_order_list'),
    path('api/orders/<int:pk>/', views.OrderDetailView.as_view(), name='api_order_detail'),
]