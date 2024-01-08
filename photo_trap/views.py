from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PhotoTrap
from .serializers import PhotoTrapSerializer

class PhotoTrapView(APIView):

    def get(self, request, mac_address):
        try:
            photo_trap = PhotoTrap.objects.get(mac_address=mac_address)
        except PhotoTrap.DoesNotExist:
            # Cria um novo registro se não existir
            photo_trap = PhotoTrap.objects.create(mac_address=mac_address)
        serializer = PhotoTrapSerializer(photo_trap)
        return Response(serializer.data)
