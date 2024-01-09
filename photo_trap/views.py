from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Photo, PhotoTrap
from .serializers import PhotoSerializer,PhotoTrapSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics

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
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        photos = Photo.objects.all()
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PhotoListView(generics.ListCreateAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    parser_classes = (MultiPartParser, FormParser)  # Necessário para o upload de imagens

    def perform_create(self, serializer):
        # Você pode adicionar lógica adicional aqui se necessário antes de salvar
        serializer.save()