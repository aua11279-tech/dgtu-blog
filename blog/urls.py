from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password/', views.password_change, name='password_change'),

    path('excursion/', views.excursion, name='excursion'),
    path('search/', views.search, name='search'),
    path('stats/', views.stats, name='stats'),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),

    path('postupayushim/', views.postupayushim, name='postupayushim'),
    path('abiturient/', views.abiturient, name='abiturient'),
    path('faculties/', views.faculties, name='faculties'),
    path('rustore/', views.rustore, name='rustore'),
]