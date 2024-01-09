from django.urls import path
from .views import PhotoTrapView, PhotoView

urlpatterns = [
    path('photo_trap/<str:mac_address>/', PhotoTrapView.as_view(), name='photo_trap'),
    path('photos/<str:mac_address>/', PhotoView.as_view(), name='photo_list'),  # nova rota para PhotoView
    path('photos/', PhotoView.as_view(), name='photos'),
]
