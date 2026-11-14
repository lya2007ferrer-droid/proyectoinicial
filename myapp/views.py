from django.shortcuts import render

from django.http import JsonResponse
from .models import areasverdes, ActividadSugerida
from django.views.decorators.http import require_POST

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
        datos.append({'id': parque.id,
            'nombre': parque.nombre,
            'comuna': parque.get_comuna_display(),
            'lat': parque.latitud,
            'lng': parque.longitud,
            'descripcion': parque.descripcion,
            'superficie_ha': float(parque.superficie_ha) if parque.superficie_ha is not None else None,
            'foto_url': parque.foto.url if parque.foto else None,
            'credito_foto': parque.credito_foto,
            'contorno_geojson': parque.contorno_geojson,
            'actividades': list(parque.actividades.values_list('nombre', flat=True)) + list(parque.actividades_sugeridas.filter(aprobada=True).values_list('nombre', flat=True))
            })

    return JsonResponse({'parques': datos})
@require_POST
def sugerir_actividad(request, parque_id):
    nombre = request.POST.get('nombre', '').strip()

    if not nombre or len(nombre) > 100:
        return JsonResponse({
            'error': 'Ingresa una actividad válida'
        }, status=400)

    parque = areasverdes.objects.filter(id=parque_id).first()

    if parque is None:
        return JsonResponse({
            'error': 'Parque no encontrado'
        }, status=404)

    ActividadSugerida.objects.create(
        parque=parque,
        nombre=nombre,
        aprobada=False
    )

    return JsonResponse({
        'mensaje': 'Sugerencia enviada correctamente'
    }, status=201)