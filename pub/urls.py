from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, MenuItemViewSet

router = DefaultRouter()
router.register(r'menu', views.MenuItemViewSet, basename='menu')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('api/', include(router.urls)),
]