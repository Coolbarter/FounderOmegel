from django.urls import path
from . import views

urlpatterns = [
    path('', views.FounderProfileListView.as_view(), name='profile_list'),  # List all profiles
    path('create/', views.FounderProfileCreateView.as_view(), name='profile_create'),
    path('update/', views.FounderProfileUpdateView.as_view(), name='profile_update'),  # Update own profile
    path('my/', views.FounderProfileDetailView.as_view(), name='profile'),  # User's own profile
    path('<int:pk>/', views.FounderProfileDetailView.as_view(), name='profile_detail'),  # Other user's profile
    path('discover/', views.FounderDiscoveryView.as_view(), name='founder_discovery'),  # Founder discovery page
] 