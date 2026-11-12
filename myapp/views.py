from django.shortcuts import render

from django.http import JsonResponse
from .models import areasverdes

def mapa_principal(request):
    comunas = areasverdes._meta.get_field('comuna').choices

    return render(request, 'myapp/mapa.html', {
        'comunas': comunas
    })

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
            'descripcion': parque.descripcion,
            'superficie_ha': float(parque.superficie_ha) if parque.superficie_ha is not None else None,
            'foto_url': parque.foto.url if parque.foto else None,
            'credito_foto': parque.credito_foto,
            'contorno_geojson': parque.contorno_geojson,
            'actividades': list(parque.actividades.values_list('nombre', flat=True))
            })

    return JsonResponse({'parques': datos})
