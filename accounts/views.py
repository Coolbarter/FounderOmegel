from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserUpdateForm, CustomPasswordChangeForm

User = get_user_model()

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('profile_create')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registration successful! Please complete your founder profile to continue.')
        return response

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirect to profile list if user has a profile, otherwise to profile creation."""
        if hasattr(self.request.user, 'founder_profile'):
            return reverse_lazy('profile_list')
        return reverse_lazy('profile_create')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Login successful!')
        return response

class CustomLogoutView(LogoutView):
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out.')
        return super().dispatch(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/change_password.html'

    def post(self, request, *args, **kwargs):
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        form = CustomPasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})
