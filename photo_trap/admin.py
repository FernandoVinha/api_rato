from django.contrib import admin
from .models import PhotoTrap, Photo

@admin.register(PhotoTrap)
class PhotoTrapAdmin(admin.ModelAdmin):
    list_display = ['mac_address', 'country', 'region', 'city', 'server_url']
    search_fields = ['mac_address', 'country__name', 'city__name']
    list_filter = ['country', 'region', 'city']

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['photo_trap', 'capture_date', 'processed']
    search_fields = ['photo_trap__mac_address', 'capture_date']
    list_filter = ['photo_trap', 'capture_date', 'processed']
