from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

urlpatterns = [
    path('photo_trap/<str:mac_address>/', PhotoTrapView.as_view(), name='photo_trap'),
    path('photos/', PhotoListView.as_view(), name='photo-list'),
    path('download_firmware/<int:firmware_id>/', FirmwareDownloadView.as_view(), name='download_firmware'),
    path('dashboard/', photo_trap_list, name='dashboard'),
    path('dashboard/customer/<int:customer_id>/', photo_trap_list, name='dashboard_by_customer'),
    path('verificar_mac_address/', verificar_mac_address, name='verificar_mac_address'),
    path('editar_phototrap/<str:pk>/', editar_phototrap, name='editar_phototrap'),
    path('phototraps/', lista_phototraps, name='lista_phototraps'),
    path('phototrap/excluir/<str:mac_address>/', excluir_phototrap, name='excluir_phototrap'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)