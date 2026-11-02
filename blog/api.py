from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.db.models.functions import Length

from .models import Article, Tag, Profile
from .serializers import (
    ArticleSerializer,
    TagSerializer,
    ProfileSerializer,
    AuthorSerializer,
)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение: редактировать статью может только автор."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class ArticleViewSet(viewsets.ModelViewSet):
    """API для статей."""

    queryset = Article.objects.with_related()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['published_date', 'title']
    ordering = ['-published_date']

    def get_queryset(self):
        qs = super().get_queryset()
        # Неавторизованные посетители видят только опубликованные статьи.
        if not self.request.user.is_authenticated:
            qs = qs.filter(is_published=True)
        else:
            # Авторизованный пользователь видит опубликованные статьи и свои черновики.
            qs = qs.filter(Q(is_published=True) | Q(author=self.request.user))
        tag = self.request.query_params.get('tag')
        author = self.request.query_params.get('author')
        search = self.request.query_params.get('search')

        if tag:
            qs = qs.filter(tags__slug=tag)
        if author:
            qs = qs.filter(author__username=author)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
        return qs

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по авторам."""
        authors = User.objects.annotate(
            article_count=Count('articles'),
            avg_length=Avg(Length('articles__content')),
        ).filter(article_count__gt=0)

        data = [
            {
                'username': a.username,
                'email': a.email,
                'article_count': a.article_count,
                'avg_length': round(a.avg_length or 0, 2),
            }
            for a in authors
        ]
        return Response(data)


class TagViewSet(viewsets.ModelViewSet):
    """API для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """Профиль может изменять только его владелец."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj.user_id == request.user.id


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Просмотр профилей и редактирование собственного профиля."""

    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly]


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """API для списка авторов (только чтение)."""

    queryset = User.objects.all()
    serializer_class = AuthorSerializer