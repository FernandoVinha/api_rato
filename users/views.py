from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserLoginForm  # Formulário personalizado para login
from .models import *
from .forms import CustomerForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def custom_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redireciona para a página inicial após o login
            else:
                # Trata o caso de falha na autenticação
                return render(request, 'login.html', {'form': form, 'error': 'Email ou senha inválidos'})
    else:
        form = CustomUserLoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def lista_clientes(request):
    # Verifica se o usuário está logado
    if request.user.is_authenticated:
        # Verifica se o usuário pertence a uma empresa
        if request.user.company:
            # Recupera o termo de busca, se existir
            search_query = request.GET.get('search', '')
            # Filtra os clientes da mesma empresa que o usuário logado, considerando o termo de busca
            clientes = Customer.objects.filter(
                Q(name__icontains=search_query) |  # Filtra por nome parecido
                Q(email__icontains=search_query) |  # Filtra por email parecido
                Q(phone_1__icontains=search_query)  # Filtra por telefone parecido
            ).filter(company=request.user.company)
            # Renderiza o template com a lista de clientes
            return render(request, 'lista_clientes.html', {'clientes': clientes})
        else:
            # Se o usuário não pertencer a nenhuma empresa, redirecione para uma página de erro ou faça outra ação adequada
            return render(request, 'pagina_de_erro.html', {'mensagem': 'Você não está associado a uma empresa.'})
    else:
        # Se o usuário não estiver logado, redireciona para a página de login
        return redirect('login')
    

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Customer, pk=cliente_id)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = CustomerForm(instance=cliente)

    return render(request, 'editar_cliente.html', {'form': form})


@login_required
def excluir_cliente(request, cliente_id):
    cliente = get_object_or_404(Customer, pk=cliente_id)

    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')

    return render(request, 'excluir_cliente.html', {'cliente': cliente})


@login_required
def adicionar_cliente(request):
    if request.method == 'POST':
        # Se o formulário for submetido com dados
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Crie uma instância do cliente, mas não o salve ainda no banco de dados
            cliente = form.save(commit=False)
            # Associe o cliente à empresa do usuário atual
            cliente.company = request.user.company
            # Salve o cliente no banco de dados
            cliente.save()
            # Redirecione para uma página de sucesso ou para a página de lista de clientes
            return redirect('lista_clientes')
        else:
            # Se o formulário não for válido, imprima uma mensagem de erro no console
            print("O formulário é inválido. Razões:")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"- {field}: {error}")
    else:
        # Se o formulário não foi submetido, crie uma instância do formulário vazio
        form = CustomerForm()
    # Renderize o template do formulário de adicionar cliente com o formulário
    return render(request, 'adicionar_cliente.html', {'form': form})