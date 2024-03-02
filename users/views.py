from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import CustomUserLoginForm  # Formulário personalizado para login


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
