from django.shortcuts import render

from django.http import JsonResponse
from .models import areasverdes

def mapa_principal(request):
#Carga la página principal con el mapa
    return render(request, 'myapp/mapa.html')

def api_obtener_parques(request):
#Filtra y devuelve los parques según la comuna seleccionada (formato JSON)
    comuna_seleccionada = request.GET.get('comuna', None)
    print(f"DEBUG - Comuna solicitada: '{comuna_seleccionada}'")

    parques = areasverdes.objects.all()

    if comuna_seleccionada and comuna_seleccionada != 'todas':
        parques = parques.filter(comuna__iexact=comuna_seleccionada)

    datos = []
    for parque in parques:
        datos.append({
            'nombre': parque.nombre,
            'comuna': parque.get_comuna_display(),
            'lat': parque.latitud,
            'lng': parque.longitud,
        })

    return JsonResponse({'parques': datos})
