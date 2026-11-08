from django.contrib import admin
from .models import areasverdes, Actividad


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
