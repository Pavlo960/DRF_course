from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"menu-items", views.MenuItemViewSet, basename="menuitem")
router.register(r"orders", views.OrderViewSet, basename="order")

urlpatterns = router.urls
