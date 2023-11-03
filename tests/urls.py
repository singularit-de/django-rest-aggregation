from rest_framework.routers import DefaultRouter

from .views import BookViewSet, StoreViewSet, AuthorViewSet, CustomizedBookViewSet

router = DefaultRouter()
router.register(r'book', BookViewSet)
router.register(r'customized_book', CustomizedBookViewSet)
router.register(r'store', StoreViewSet)
router.register(r'author', AuthorViewSet)

urlpatterns = router.urls
