from django.urls import path
from .views import PhotoTrapView, PhotoView,PhotoListView


urlpatterns = [
    path('photo_trap/<str:mac_address>/', PhotoTrapView.as_view(), name='photo_trap'),
    path('photos/', PhotoListView.as_view(), name='photo-list'),
]
