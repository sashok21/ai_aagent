from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Головна сторінка
    path('', views.HomePageView.as_view(), name='home'),

    # Маршрути
    path('routes/', views.RoutesListView.as_view(), name='routes-list'),
    path('routes/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),

    # Відгуки
    path('routes/<int:route_id>/review/add/', views.ReviewCreateView.as_view(), name='review-create'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),

    # Профіль та аутентифікація
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='mountains_roads/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile-edit'),

    # Улюблені та пройдені маршрути
    path('routes/<int:route_id>/toggle-favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('routes/<int:route_id>/toggle-completed/', views.toggle_completed, name='toggle-completed'),
]