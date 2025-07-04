from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, UpdateView
from .forms import UserLoginForm, UserRegistrationForm
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class RegisterView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'user_obj'

    def get_object(self):
        return self.request.user

class UserEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ['username', 'email', 'avatar']
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

# class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
#     form_class = CustomPasswordChangeForm
#     template_name = 'accounts/change_password.html'
#     success_url = reverse_lazy('profile')
