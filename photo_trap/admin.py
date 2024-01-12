from django.contrib import admin
from .models import PhotoTrap, Photo

@admin.register(PhotoTrap)
class PhotoTrapAdmin(admin.ModelAdmin):
    list_display = [
        'mac_address', 'country', 'region', 'city', 
        'photo_url', 'firmware_url', 'latitude', 'longitude', 'floor'
    ]
    search_fields = ['mac_address', 'country__name', 'city__name', 'region__name']
    list_filter = ['country', 'region', 'city', 'movement_sensor', 'restart', 'install_new_firmware']

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['photo_trap', 'capture_date', 'processed']
    search_fields = ['photo_trap__mac_address', 'capture_date']
    list_filter = ['photo_trap', 'capture_date', 'processed']
