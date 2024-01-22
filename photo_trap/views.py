from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Photo, PhotoTrap
from .serializers import PhotoSerializer,PhotoTrapSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from rest_framework.exceptions import ValidationError


class PhotoTrapView(APIView):

    def get(self, request, mac_address):
        try:
            photo_trap = PhotoTrap.objects.get(mac_address=mac_address)
        except PhotoTrap.DoesNotExist:
            photo_trap = PhotoTrap.objects.create(mac_address=mac_address)

        # Serializa os dados antes de alterar o valor de install_new_firmware
        serializer = PhotoTrapSerializer(photo_trap)
        response = Response(serializer.data)

        # Agora atualiza o valor de install_new_firmware, se necessário
        if photo_trap.install_new_firmware:
            photo_trap.install_new_firmware = False
            photo_trap.save()

        return response



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
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print("Erro no formulário: ", request.data)
            print("Detalhes do erro: ", e.detail)
            raise e  # Re-lança a exceção para que seja manuseada pelo framework
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()