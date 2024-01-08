from django.urls import path
from .views import PhotoTrapView

urlpatterns = [
    path('photo_trap/<str:mac_address>/', PhotoTrapView.as_view(), name='photo_trap'),
]
