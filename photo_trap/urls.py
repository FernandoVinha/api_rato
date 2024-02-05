from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import PhotoTrapView, PhotoListView, FirmwareDownloadView

urlpatterns = [
    path('photo_trap/<str:mac_address>/', PhotoTrapView.as_view(), name='photo_trap'),
    path('photos/', PhotoListView.as_view(), name='photo-list'),
     path('download_firmware/<int:firmware_id>/', FirmwareDownloadView.as_view(), name='download_firmware'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)