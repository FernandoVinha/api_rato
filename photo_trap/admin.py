from django.contrib import admin
from .models import PhotoTrap

@admin.register(PhotoTrap)
class PhotoTrapAdmin(admin.ModelAdmin):
    list_display = ['mac_address', 'ntp_server', 'gmt_offset', 'daylight_offset', 'movement_sensor', 'restart', 'photo_shooting_frequency', 'latitude', 'longitude', 'floor', 'server_url', 'firmware_path', 'install_new_firmware']
