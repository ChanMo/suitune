from django.urls import path
from .views import NextTrackView, FeedbackView, FavoritesListView

urlpatterns = [
    path('next', NextTrackView.as_view(), name='next-track'),
    path('feedback', FeedbackView.as_view(), name='feedback'),
    path('favorites', FavoritesListView.as_view(), name='favorites-list'),
]
