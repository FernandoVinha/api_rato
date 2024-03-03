from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Photo, PhotoTrap
from .serializers import PhotoSerializer,PhotoTrapSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.views import View
from .models import Firmware
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from users.models import Customer
from django.db.models import F
import folium
from django.db.models import Q
from django.contrib import messages

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

@login_required
def verificar_mac_address(request):
    if request.method == 'POST':
        mac_address = request.POST.get('mac_address')
        try:
            phototrap = PhotoTrap.objects.get(mac_address=mac_address)
            # Redirecionar para a view editar_phototrap com o pk do PhotoTrap encontrado
            return redirect('editar_phototrap', pk=phototrap.pk)
        except PhotoTrap.DoesNotExist:
            # Lógica para lidar com o caso em que o PhotoTrap não existe
            pass
    return render(request, 'verificar_mac_address.html')

@login_required
def editar_phototrap(request, pk):
    phototrap = PhotoTrap.objects.get(pk=pk)

    # Verifica se o usuário está associado a uma empresa
    if request.user.company:
        company = request.user.company

        # Verifica se o usuário pertence à mesma empresa do PhotoTrap ou se é superusuário
        if request.user.is_superuser or phototrap.company == company:
            if request.method == 'POST':
                phototrap.latitude = request.POST.get('latitude')
                phototrap.longitude = request.POST.get('longitude')
                phototrap.floor = request.POST.get('floor')
                phototrap.country = request.POST.get('country')
                phototrap.region_id = request.POST.get('region')
                phototrap.city_id = request.POST.get('city')
                
                # Verifica se o customer_id pertence à mesma empresa do usuário
                customer_id = request.POST.get('customer')
                if customer_id:
                    customer = Customer.objects.filter(company=company, pk=customer_id).first()
                    phototrap.customer = customer
                else:
                    phototrap.customer = None

                phototrap.save()
                return redirect('pagina_sucesso')  # Redireciona para página de sucesso após edição

            # Recupera todos os clientes associados à empresa do usuário para serem exibidos no formulário
            customers = Customer.objects.filter(company=company)

            return render(request, 'editar_phototrap.html', {'phototrap': phototrap, 'customers': customers})

    # Se o usuário não está associado a uma empresa ou não tem permissão para editar o PhotoTrap,
    # redirecionar para uma página de erro ou fazer outra ação adequada
    return render(request, 'dashboard', {'mensagem': 'Você não tem permissão para editar este PhotoTrap.'})

@login_required
def lista_phototraps(request):
    # Verifica se o usuário está logado
    if request.user.is_authenticated:
        # Verifica se o usuário pertence a uma empresa
        if request.user.company:
            # Recupera o termo de busca, se existir
            search_query = request.GET.get('search', '')
            # Filtra os PhotoTraps da mesma empresa que o usuário logado, considerando o termo de busca
            phototraps = PhotoTrap.objects.filter(
                Q(mac_address__icontains=search_query) |  # Filtra por endereço MAC parecido
                Q(latitude__icontains=search_query) |  # Filtra por latitude parecida
                Q(longitude__icontains=search_query)  # Filtra por longitude parecida
            ).filter(company=request.user.company)
            # Renderiza o template com a lista de PhotoTraps
            return render(request, 'lista_phototraps.html', {'phototraps': phototraps})
        else:
            # Se o usuário não pertencer a nenhuma empresa, redirecione para uma página de erro ou faça outra ação adequada
            return render(request, 'pagina_de_erro.html', {'mensagem': 'Você não está associado a uma empresa.'})
    else:
        # Se o usuário não estiver logado, redireciona para a página de login
        return redirect('login')
    
@login_required
def excluir_phototrap(request, mac_address):
    phototrap = get_object_or_404(PhotoTrap, mac_address=mac_address)
    
    # Verifica se o usuário tem permissão para excluir o PhotoTrap
    if request.user.is_superuser or (request.user.company and request.user.company == phototrap.company):
        phototrap.delete()
        messages.success(request, "PhotoTrap excluído com sucesso.")
    else:
        messages.error(request, "Você não tem permissão para excluir este PhotoTrap.")

    return redirect('lista_phototraps')