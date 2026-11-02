from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class ArticleQuerySet(models.QuerySet):
    """Кастомный QuerySet с методами фильтрации."""

    def published(self):
        return self.filter(is_published=True)

    def by_author(self, username):
        return self.filter(author__username=username)

    def with_related(self):
        return self.select_related('author').prefetch_related('tags')


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='articles',
        blank=True,
        verbose_name='Теги'
    )
    published_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ['-published_date']
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return f'Профиль {self.user.username}'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()