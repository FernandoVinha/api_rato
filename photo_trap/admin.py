from django.contrib import admin
from .models import PhotoTrap, Photo, Firmware

# Register PhotoTrap model
@admin.register(PhotoTrap)
class PhotoTrapAdmin(admin.ModelAdmin):
    list_display = ['mac_address', 'ntp_url', 'status', 'company', 'customer']
    list_filter = ['status', 'company', 'customer']
    search_fields = ['mac_address', 'company__name', 'customer__name']
    # Add more configurations as needed

# Register Photo model
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['photo_trap', 'capture_date', 'processed']
    list_filter = ['processed']
    search_fields = ['photo_trap__mac_address']
    # Add more configurations as needed

# Register Firmware model
@admin.register(Firmware)
class FirmwareAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'release_date']
    search_fields = ['name', 'version']
    # Add more configurations as needed
