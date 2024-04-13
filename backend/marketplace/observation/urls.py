from django.urls import path

from .views import ObservationView

urlpatterns = [
    path('observation', ObservationView.as_view(), name='observation')
]