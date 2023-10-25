from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PublisherViewSet, BookViewSet, StoreViewSet

router = DefaultRouter()
router.register(r'publisher', PublisherViewSet)
router.register(r'book', BookViewSet)
router.register(r'store', StoreViewSet)

urlpatterns = router.urls
