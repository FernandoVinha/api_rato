from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Photo, PhotoTrap
from .serializers import PhotoSerializer,PhotoTrapSerializer
from django.shortcuts import get_object_or_404



class PhotoTrapView(APIView):

    def get(self, request, mac_address):
        try:
            photo_trap = PhotoTrap.objects.get(mac_address=mac_address)
        except PhotoTrap.DoesNotExist:
            # Cria um novo registro se não existir
            photo_trap = PhotoTrap.objects.create(mac_address=mac_address)
        serializer = PhotoTrapSerializer(photo_trap)
        return Response(serializer.data)


class PhotoView(APIView):
    def get(self, request):
        photos = Photo.objects.all()
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)