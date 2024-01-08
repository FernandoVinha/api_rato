from rest_framework import serializers
from .models import PhotoTrap

class PhotoTrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTrap
        fields = '__all__'
