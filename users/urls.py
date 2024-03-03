from django.urls import path
from .views import *

urlpatterns = [
    # ... outras urls ...
    path('', custom_login, name='login'),
    path('clientes/', lista_clientes, name='lista_clientes'),
    path('clientes/<int:cliente_id>/editar/', editar_cliente, name='editar_cliente'),
    path('clientes/<int:cliente_id>/excluir/', excluir_cliente, name='excluir_cliente'),
     path('clientes/adicionar/', adicionar_cliente, name='adicionar_cliente'),
]
