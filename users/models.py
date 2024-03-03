from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    address = models.CharField(max_length=255, verbose_name='Endereço')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    phone = models.CharField(max_length=15, verbose_name='Telefone')
    image = models.ImageField(upload_to='Company/', blank=True, null=True)  # Novo campo para imagem

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O endereço de e-mail deve ser fornecido'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser deve ter is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(_('endereço de e-mail'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='CustomUser/', blank=True, null=True)  # Novo campo para imagem
    level = models.IntegerField(default=0,validators=[MinValueValidator(0), MaxValueValidator(10)])

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_1 = models.CharField(max_length=15,blank=True, null=True)
    phone_2 = models.CharField(max_length=15, blank=True, null=True)  # Campo opcional
    address = models.CharField(max_length=255, blank=True)
    CNPJ = models.CharField(max_length=18,blank=True, null=True)
    contact_1 = models.CharField(max_length=100, blank=True, null=True)  # Campo opcional
    contact_2 = models.CharField(max_length=100, blank=True, null=True)  # Campo opcional
    contact_3 = models.CharField(max_length=100, blank=True, null=True)  # Campo opcional
    activity = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='customer_images/', blank=True, null=True)  # Novo campo para imagem

    def __str__(self):
        return self.name