from django.contrib.auth.views import PasswordResetDoneView
from django.urls import path
from . import views



app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name = 'login'),
    path('registration/', views.RegisterView.as_view(), name = 'registration'),
    path('profile/', views.UserProfileView.as_view(), name = 'profile'),
]