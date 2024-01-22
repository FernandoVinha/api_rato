from django.db import models
from django_countries.fields import CountryField
from cities_light.models import City, Region
from django.utils import timezone

class PhotoTrap(models.Model):
    mac_address = models.CharField(max_length=255, primary_key=True)
    ntp_url = models.CharField(max_length=255, default="pool.ntp.org")
    gmt_offset = models.IntegerField(default=-3)
    daylight_offset = models.IntegerField(default=0)
    movement_sensor = models.BooleanField(default=False)
    restart = models.BooleanField(default=False)
    photo_shooting_frequency = models.CharField(max_length=255, default='["00:00","12:00"]')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    floor = models.FloatField(default=0.0)
    photo_url = models.CharField(max_length=255, default="177.73.234.198")
    photo_path = models.CharField(max_length=255, default="/photos/")
    photo_port = models.IntegerField(default=88)
    firmware_url = models.CharField(max_length=255, default="https://raw.githubusercontent.com/FernandoVinha/api_rato/main/")
    firmware_path = models.CharField(max_length=255, default="get_test_09.ino.esp32.bin")
    install_new_firmware = models.BooleanField(default=True)
    country = CountryField(blank_label='(select country)', default='BR')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)


class Photo(models.Model):
    photo_trap = models.ForeignKey(PhotoTrap, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/')
    capture_date = models.DateTimeField(default=timezone.now)  # Ajuste aqui
    processed = models.BooleanField(default=False)
