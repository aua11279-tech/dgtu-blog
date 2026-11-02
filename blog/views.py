from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.views.generic import ListView

from .forms import (
    CustomUserCreationForm,
    ProfileForm,
    CustomPasswordChangeForm,
)
from .models import Article


def home(request):
    articles = Article.objects.published().with_related()
    if not articles.exists():
        articles = []
    context = {'news_list': articles}
    return render(request, 'blog/home.html', context)


class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.published().with_related()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'blog/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'blog/profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'blog/profile_edit.html', {'form': form})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль изменён')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'blog/password_change.html', {'form': form})


def excursion(request):
    return render(request, 'blog/excursion.html')


def search(request):
    q = request.GET.get('q', '').strip()
    articles = Article.objects.none()
    if q:
        articles = Article.objects.published().with_related().filter(
            Q(title__icontains=q) | Q(content__icontains=q) | Q(tags__name__icontains=q)
        ).distinct()
    context = {'articles': articles, 'q': q}
    return render(request, 'blog/search.html', context)


def stats(request):
    authors = User.objects.annotate(
        article_count=Count('articles'),
        avg_length=Avg('articles__content'),
    ).filter(article_count__gt=0).order_by('-article_count')
    context = {'authors': authors}
    return render(request, 'blog/stats.html', context)


def postupayushim(request):
    return render(request, 'blog/postupayushim.html')


def abiturient(request):
    return render(request, 'blog/abiturient.html')


def faculties(request):
    return render(request, 'blog/faculties.html')


def rustore(request):
    return render(request, 'blog/rustore.html')