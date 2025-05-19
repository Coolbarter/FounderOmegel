from django.urls import path
from . import views

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('create/<int:founder_id>/', views.MatchCreateView.as_view(), name='match_create'),
    path('detail/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('update/<int:pk>/', views.MatchUpdateView.as_view(), name='match_update'),
    path('response/<int:pk>/', views.MatchResponseView.as_view(), name='match_response'),
] 