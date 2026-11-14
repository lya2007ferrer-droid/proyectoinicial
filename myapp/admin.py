from django.contrib import admin
from .models import areasverdes, Actividad,ActividadSugerida


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(areasverdes)
class AreasVerdesAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'comuna']
    search_fields = ['nombre']
    list_filter = ['comuna', 'actividades']
    filter_horizontal = ['actividades']
# Register your models here.

@admin.register(ActividadSugerida)
class ActividadSugeridaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'parque', 'aprobada', 'creada']
    list_filter = ['aprobada', 'creada']
    search_fields = ['nombre', 'parque__nombre']
    list_editable = ['aprobada']