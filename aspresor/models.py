from django.db import models
from django_countries.fields import CountryField
from cities_light.models import City, Region
from django.utils import timezone

class Aspresor(models.Model):
    mac_address = models.CharField(max_length=255, primary_key=True)
    ntp_url = models.CharField(max_length=255, default="pool.ntp.org")
    gmt_offset = models.IntegerField(default=-3)
    daylight_offset = models.IntegerField(default=0)
    restart = models.BooleanField(default=False)
    on_off_A = models.CharField(max_length=255, default='["00:00","12:00"]')
    on_off_B = models.CharField(max_length=255, default='["00:00","12:00"]')
    level_A = models.IntegerField(default=0)
    level_B = models.IntegerField(default=0)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    floor = models.FloatField(default=0.0)
    firmware_url = models.CharField(max_length=255, default="https://github.com/FernandoVinha/api_rato")
    firmware_path = models.CharField(max_length=255, default="/firmware.bin")
    install_new_firmware = models.BooleanField(default=False)
    country = CountryField(blank_label='(select country)', default='BR')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)