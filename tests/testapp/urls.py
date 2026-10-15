from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet, CustomizedBookViewSet, StoreViewSet

router = DefaultRouter()
router.register(r"book", BookViewSet)
router.register(r"customized_book", CustomizedBookViewSet, basename="customized_book")
router.register(r"store", StoreViewSet)
router.register(r"author", AuthorViewSet)

urlpatterns = router.urls
