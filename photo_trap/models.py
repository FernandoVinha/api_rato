from django.db import models
from django_countries.fields import CountryField
from cities_light.models import City, Region

class PhotoTrap(models.Model):
    mac_address = models.CharField(max_length=255, primary_key=True)
    ntp_server = models.CharField(max_length=255, default="http://pool.ntp.org/")
    gmt_offset = models.IntegerField(default=-3)
    daylight_offset = models.IntegerField(default=0)
    movement_sensor = models.BooleanField(default=False)
    restart = models.CharField(max_length=255, default="False")
    photo_shooting_frequency = models.CharField(max_length=255, default='"12:00","24:00"')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    floor = models.FloatField(default=0.0)
    server_url = models.CharField(max_length=255, default="192.168.0.1")
    firmware_path = models.CharField(max_length=255, default="https://github.com/FernandoVinha/PhotoTrapFirmware")
    install_new_firmware = models.BooleanField(default=False)
    country = CountryField(blank_label='(select country)', default='BR')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
