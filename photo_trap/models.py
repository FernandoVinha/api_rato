from django.db import models
from django_countries.fields import CountryField
from cities_light.models import City, Region
from django.utils import timezone
from users import *
STATUS_CHOICES = [
    (0, 'Offline'),
    (1, 'With Issues'),
    (2, 'Attention Needed'),
    (3, 'Operational'),
]


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
    company = models.ForeignKey('users.Company', on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey('users.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=3)
    TRAP_STATUS_CHOICES = [
        ('NONE', 'None'),
        ('T_REX_OK', 'T-Rex OK'),
        ('T_REX_DISARMED', 'T-Rex Disarmed'),
        ('GLUE_OK', 'Glue OK'),
        ('RAT_ON_GLUE', 'Rat on Glue'),
        ('GLUE_WITH_DUST', 'Glue with Dust'),
        ('POISON_OK', 'Poison OK'),
        ('LITTLE_POISON', 'Little Poison'),
        ('MOLDY_POISON', 'Moldy Poison'),
    ]

    # Adicionando o novo campo de escolha
    trap_status = models.CharField(
        max_length=20,
        choices=TRAP_STATUS_CHOICES,
        default='NONE',
    )


class Photo(models.Model):
    photo_trap = models.ForeignKey(PhotoTrap, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/')
    capture_date = models.DateTimeField(default=timezone.now)  # Ajuste aqui
    processed = models.BooleanField(default=False)

class Firmware(models.Model):
    name = models.CharField(max_length=255)
    firmware_file = models.FileField(upload_to='firmwares/')
    version = models.CharField(max_length=50)
    release_date = models.DateTimeField(default=timezone.now)
    compatible_devices = models.ManyToManyField(PhotoTrap)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - Version {self.version}"


