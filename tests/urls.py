from rest_framework.routers import DefaultRouter

from .views import BookViewSet, StoreViewSet

router = DefaultRouter()
router.register(r'book', BookViewSet)
router.register(r'store', StoreViewSet)

urlpatterns = router.urls
