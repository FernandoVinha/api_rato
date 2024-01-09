from rest_framework import serializers
from .models import PhotoTrap,Photo


class PhotoTrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTrap
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'