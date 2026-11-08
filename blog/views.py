import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.views.generic import ListView
from django.core.mail import send_mail, EmailMessage  # Добавили EmailMessage
from django.conf import settings
from django.contrib.auth.views import LoginView

from .forms import (
    CustomUserCreationForm,
    ProfileForm,
    OTPForm,
    CustomPasswordChangeForm,
)
from .models import Article

def home(request):
    articles = Article.objects.published().with_related()
    context = {'news_list': articles}
    return render(request, 'blog/home.html', context)

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    def get_queryset(self):
        return Article.objects.published().with_related()

# === РЕГИСТРАЦИЯ С 2FA ===
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Блокируем до подтверждения
            user.save()
            
            profile = user.profile
            profile.otp_code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            profile.save()
            
            # Используем EmailMessage с кодировкой utf-8
            email = EmailMessage(
                subject='Подтверждение регистрации',
                body=f'Ваш код подтверждения: {profile.otp_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.encoding = 'utf-8'
            email.send()
            
            request.session['verify_user_id'] = user.id
            messages.info(request, 'Код отправлен на вашу почту.')
            return redirect('verify_otp')
    else:
        form = CustomUserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

# === КАСТОМНЫЙ ВХОД С 2FA ===
class CustomLoginView(LoginView):
    template_name = 'blog/login.html'

    def form_valid(self, form):
        user = form.get_user()
        profile = user.profile
        profile.otp_code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        profile.save()
        
        # Используем EmailMessage с кодировкой utf-8
        email = EmailMessage(
            subject='Код для входа',
            body=f'Ваш код для входа: {profile.otp_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.encoding = 'utf-8'
        email.send()
        
        self.request.session['verify_user_id'] = user.id
        return redirect('verify_otp')

# === ПРОВЕРКА КОДА ===
def verify_otp(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            profile = user.profile
            
            if profile.otp_code == entered_code:
                if not profile.email_verified:
                    profile.email_verified = True
                    user.is_active = True
                    user.save()
                
                profile.otp_code = None
                profile.save()
                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['verify_user_id']
                messages.success(request, 'Успешный вход!')
                return redirect('home')
            else:
                messages.error(request, 'Неверный код. Попробуйте снова.')
    else:
        form = OTPForm()
    return render(request, 'blog/otp_verify.html', {'form': form})

# === ОСТАЛЬНЫЕ ФУНКЦИИ ===
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
    return render(request, 'blog/search.html', {'articles': articles, 'q': q})

def stats(request):
    authors = User.objects.annotate(
        article_count=Count('articles'),
        avg_length=Avg('articles__content'),
    ).filter(article_count__gt=0).order_by('-article_count')
    return render(request, 'blog/stats.html', {'authors': authors})

def postupayushim(request):
    return render(request, 'blog/postupayushim.html')

def abiturient(request):
    return render(request, 'blog/abiturient.html')

def faculties(request):
    return render(request, 'blog/faculties.html')

def rustore(request):
    return render(request, 'blog/rustore.html')

def college_joke(request):
    return render(request, 'blog/college_joke.html')
def clown_joke(request):
    return render(request, 'blog/clown_joke.html')
# ... (твой предыдущий код) ...

def branches(request):
    return render(request, 'blog/branches.html')

def education(request):
    return render(request, 'blog/education.html')