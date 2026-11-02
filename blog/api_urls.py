from rest_framework.routers import DefaultRouter
from .api import ArticleViewSet, TagViewSet, ProfileViewSet, AuthorViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='article')
router.register('tags', TagViewSet, basename='tag')
router.register('profiles', ProfileViewSet, basename='profile')
router.register('authors', AuthorViewSet, basename='author')

urlpatterns = router.urls