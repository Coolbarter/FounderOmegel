from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DetailView, TemplateView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
import os
import re
import pytz
from .models import FounderProfile
from .forms import FounderProfileForm, FounderProfileRegistrationForm

# Create your views here.

class FounderProfileCreateView(LoginRequiredMixin, CreateView):
    model = FounderProfile
    form_class = FounderProfileRegistrationForm
    template_name = 'profiles/profile_registration.html'
    success_url = reverse_lazy('founder_discovery')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Profile created successfully! You can now discover other founders.')
        return response

    def get(self, request, *args, **kwargs):
        # Check if user already has a profile
        if hasattr(request.user, 'founder_profile'):
            messages.info(request, 'You already have a profile.')
            return redirect('profile_update')
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class FounderProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = FounderProfile
    form_class = FounderProfileForm
    template_name = 'profiles/profile_form.html'

    def get_success_url(self):
        return reverse('profile')  # This will redirect to the user's own profile

    def get_object(self, queryset=None):
        return get_object_or_404(FounderProfile, user=self.request.user)

    def form_valid(self, form):
        # Handle file upload
        if 'profile_picture' in self.request.FILES:
            # Delete old profile picture if it exists
            if self.object.profile_picture:
                try:
                    old_file_path = self.object.profile_picture.path
                    if os.path.isfile(old_file_path):
                        os.remove(old_file_path)
                except Exception as e:
                    print(f"Error deleting old profile picture: {e}")
            
            # Clean the filename
            profile_pic = self.request.FILES['profile_picture']
            clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', profile_pic.name)
            profile_pic.name = clean_filename
            
            # Save new profile picture
            form.instance.profile_picture = profile_pic
        
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class FounderProfileDetailView(LoginRequiredMixin, DetailView):
    model = FounderProfile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'founder_profile'

    def get_object(self, queryset=None):
        if 'pk' in self.kwargs:
            return get_object_or_404(FounderProfile, pk=self.kwargs['pk'])
        return get_object_or_404(FounderProfile, user=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            messages.info(request, 'Please create your founder profile first.')
            return redirect('profile_create')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['is_own_profile'] = self.object.user == self.request.user
        return context

class FounderDiscoveryView(LoginRequiredMixin, ListView):
    model = FounderProfile
    template_name = 'profiles/founder_discovery.html'
    context_object_name = 'profiles'
    paginate_by = 10

    def get_queryset(self):
        queryset = FounderProfile.objects.exclude(user=self.request.user)
        
        # Get user's interests and looking_for
        user_profile = get_object_or_404(FounderProfile, user=self.request.user)
        user_interests = user_profile.interests
        user_looking_for = user_profile.looking_for

        # Filter based on search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Filter based on interests
        interests = self.request.GET.getlist('interests')
        if interests:
            queryset = queryset.filter(interests__overlap=interests)

        # Filter based on looking_for
        looking_for = self.request.GET.getlist('looking_for')
        if looking_for:
            queryset = queryset.filter(looking_for__overlap=looking_for)

        # Filter based on location
        timezone = self.request.GET.get('timezone')
        if timezone:
            queryset = queryset.filter(timezone=timezone)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interest_choices'] = FounderProfile.INTEREST_CHOICES
        context['looking_for_choices'] = FounderProfile.LOOKING_FOR_CHOICES
        return context

class FounderProfileListView(LoginRequiredMixin, ListView):
    model = FounderProfile
    template_name = 'profiles/profile_list.html'
    context_object_name = 'profiles'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job_title_choices'] = FounderProfile.JOB_CHOICES
        return context

    def get_queryset(self):
        queryset = FounderProfile.objects.exclude(user=self.request.user)
        
        # Filter based on search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(company_name__icontains=search_query)
            )

        # Filter based on job title
        job_title = self.request.GET.get('job_title')
        if job_title:
            queryset = queryset.filter(job_title=job_title)

        # Filter based on interests
        interests = self.request.GET.getlist('interests')
        if interests:
            queryset = queryset.filter(interests__overlap=interests)

        # Filter based on looking_for
        looking_for = self.request.GET.getlist('looking_for')
        if looking_for:
            queryset = queryset.filter(looking_for__overlap=looking_for)

        # Filter based on location
        timezone = self.request.GET.get('timezone')
        if timezone:
            queryset = queryset.filter(timezone=timezone)

        return queryset
