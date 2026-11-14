from django.urls import path
from . import views

urlpatterns = [
    #página del mapa
    path('', views.mapa_principal, name='mapa_principal'),
    
    #ruta api para los filtros
    path('api/parques/', views.api_obtener_parques, name='api_parques'),
    #ruta para sugerir actividades
    path('api/parques/<int:parque_id>/sugerir/', views.sugerir_actividad, name='sugerir_actividad'),
    ]