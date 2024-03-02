from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Photo, PhotoTrap
from .serializers import PhotoSerializer,PhotoTrapSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.views import View
from .models import Firmware
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from users.models import Customer
from django.db.models import F
import folium


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

class FirmwareDownloadView(View):
    def get(self, request, firmware_id):
        try:
            firmware = Firmware.objects.get(id=firmware_id)
            file_path = firmware.firmware_file.path
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=firmware.firmware_file.name)
        except Firmware.DoesNotExist:
            raise Http404("Firmware not found.")
        

@login_required
def photo_trap_list(request):
    user_company = request.user.company
    customers = Customer.objects.filter(company=user_company)
    customer_id = request.GET.get('customer')

    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id, company=user_company)
        photo_traps = PhotoTrap.objects.filter(company=user_company, customer=customer)
    else:
        photo_traps = PhotoTrap.objects.filter(company=user_company)

    # Calcular a média das coordenadas
    latitudes = [trap.latitude for trap in photo_traps if trap.latitude and trap.longitude]
    longitudes = [trap.longitude for trap in photo_traps if trap.latitude and trap.longitude]
    
    if latitudes and longitudes:
        avg_lat = sum(latitudes) / len(latitudes)
        avg_lng = sum(longitudes) / len(longitudes)
        start_location = [avg_lat, avg_lng]
    else:
        # Valores padrão se não houver sensores com coordenadas válidas
        start_location = [-15.788497, -47.879873]  # Coordenadas de exemplo

    # Criação do mapa com Folium com zoom inicial definido para 6
    m = folium.Map(location=start_location, zoom_start=6)

    for trap in photo_traps:
        if trap.latitude and trap.longitude:
            folium.Marker(
                [trap.latitude, trap.longitude],
                popup=f'MAC: {trap.mac_address}<br>Status: {trap.get_status_display()}',
                icon=folium.Icon(color='green' if trap.status == 3 else 'red' if trap.status == 1 else 'orange' if trap.status == 2 else 'gray')
            ).add_to(m)

    # Renderizar mapa para HTML
    map_html = m._repr_html_()

    return render(request, 'photo_trap_list.html', {
        'photo_traps': photo_traps,
        'customers': customers,
        'selected_customer': customer_id,
        'map': map_html,
    })