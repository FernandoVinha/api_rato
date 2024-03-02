from django.urls import path
from .views import custom_login

urlpatterns = [
    # ... outras urls ...
    path('', custom_login, name='login'),
]
