from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Match
from .forms import MatchForm, MatchResponseForm
from profiles.models import FounderProfile

class RequireProfileMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'founder_profile'):
            messages.info(request, 'To connect with other founders, please complete your profile first.')
            return redirect('profile_create')
        return super().dispatch(request, *args, **kwargs)

class MatchListView(RequireProfileMixin, LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matchmaking/match_list.html'
    context_object_name = 'matches'
    paginate_by = 10

    def get_queryset(self):
        return Match.objects.filter(
            Q(founder1=self.request.user) |
            Q(founder2=self.request.user)
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = dict(Match.STATUS_CHOICES)
        return context

class MatchDetailView(RequireProfileMixin, LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'matchmaking/match_detail.html'
    context_object_name = 'match'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.get_object()
        
        # Determine which user is the other one
        if match.founder1 == self.request.user:
            other_founder = match.founder2
        else:
            other_founder = match.founder1
            
        context['other_founder'] = other_founder
        context['other_profile'] = other_founder.founder_profile
        context['response_form'] = MatchResponseForm()
        return context

class MatchCreateView(RequireProfileMixin, LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchForm
    template_name = 'matchmaking/match_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['founder'] = get_object_or_404(FounderProfile, id=self.kwargs['founder_id'])
        return context

    def form_valid(self, form):
        founder2_profile = get_object_or_404(FounderProfile, id=self.kwargs['founder_id'])
        
        # Calculate match score and common interests using profiles for scoring
        match_score = self.calculate_match_score(self.request.user.founder_profile, founder2_profile)
        common_interests = self.get_common_interests(self.request.user.founder_profile, founder2_profile)
        
        match = form.save(commit=False)
        match.founder1 = self.request.user
        match.founder2 = founder2_profile.user
        match.match_score = match_score
        match.common_interests = common_interests
        match.status = 'pending'
        match.save()
        
        messages.success(self.request, 'Match request sent successfully!')
        return redirect('match_detail', pk=match.pk)

    def calculate_match_score(self, founder1_profile, founder2_profile):
        # Calculate match score based on profiles
        common_interests_count = len(
            set(founder1_profile.interests) & set(founder2_profile.interests)
        )
        looking_for_match = len(
            set(founder1_profile.looking_for) & set(founder2_profile.looking_for)
        )
        return (common_interests_count * 0.6 + looking_for_match * 0.4) * 100

    def get_common_interests(self, founder1_profile, founder2_profile):
        # Find actual common interests between the two profiles
        return list(set(founder1_profile.interests) & set(founder2_profile.interests))

class MatchUpdateView(RequireProfileMixin, LoginRequiredMixin, UpdateView):
    model = Match
    form_class = MatchForm
    template_name = 'matchmaking/match_form.html'

    def get_queryset(self):
        return Match.objects.filter(founder1=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Match updated successfully!')
        return super().form_valid(form)

class MatchResponseView(RequireProfileMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        match = get_object_or_404(Match, pk=pk, founder2=request.user)
        form = MatchResponseForm(request.POST)
        
        if form.is_valid():
            response = form.cleaned_data['response']
            notes = form.cleaned_data['notes']
            
            if response == 'accept':
                match.status = 'accepted'
                messages.success(request, 'Match accepted successfully!')
            else:
                match.status = 'rejected'
                messages.info(request, 'Match declined.')
            
            if notes:
                match.notes = notes
            match.save()
            
            return redirect('match_detail', pk=match.pk)
        
        messages.error(request, 'Invalid form submission.')
        return redirect('match_detail', pk=match.pk)
