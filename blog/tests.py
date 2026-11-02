from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Article, Tag, Profile


class ProfileModelTest(TestCase):
    """Тесты модели Profile."""

    def test_profile_created_automatically(self):
        """Профиль создаётся автоматически при создании пользователя."""
        user = User.objects.create_user('testuser', 'test@mail.ru', 'Pass12345!')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user, user)


class ArticleModelTest(TestCase):
    """Тесты модели Article."""

    def setUp(self):
        self.user = User.objects.create_user('author', 'author@mail.ru', 'Pass12345!')
        self.article = Article.objects.create(
            title='Тестовая статья',
            content='Это тестовое содержание.',
            author=self.user,
            is_published=True,
        )

    def test_article_str(self):
        """__str__ возвращает заголовок."""
        self.assertEqual(str(self.article), 'Тестовая статья')

    def test_published_queryset(self):
        """Метод published() возвращает только опубликованные."""
        Article.objects.create(
            title='Черновик', content='...', author=self.user, is_published=False
        )
        published = Article.objects.published()
        self.assertEqual(published.count(), 1)
        self.assertEqual(published.first().title, 'Тестовая статья')


class ViewsTest(TestCase):
    """Тесты views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('tester', 'tester@mail.ru', 'Pass12345!')

    def test_home_page(self):
        """Главная страница открывается."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        """Страница регистрации открывается."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        """Кабинет требует авторизации."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_profile_after_login(self):
        """Залогиненный пользователь видит кабинет."""
        self.client.login(username='tester', password='Pass12345!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_search_page(self):
        """Поиск работает."""
        response = self.client.get(reverse('search') + '?q=test')
        self.assertEqual(response.status_code, 200)

    def test_stats_page(self):
        """Страница статистики работает."""
        response = self.client.get(reverse('stats'))
        self.assertEqual(response.status_code, 200)


class APITest(TestCase):
    """Тесты API."""

    def setUp(self):
        self.user = User.objects.create_user('apiuser', 'api@mail.ru', 'Pass12345!')
        self.article = Article.objects.create(
            title='API статья', content='...', author=self.user, is_published=True
        )

    def test_api_articles_list(self):
        """API возвращает список статей."""
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)

    def test_api_tags_list(self):
        """API возвращает список тегов."""
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, 200)