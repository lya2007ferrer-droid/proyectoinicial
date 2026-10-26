from django.db import models

class areasverdes(models.Model):
    Comunas = [
        ("SANTIAGO", "SANTIAGO CENTRO"),
        ("PROVIDENCIA", "PROVIDENCIA"),
        ("LAS CONDES", "LAS CONDES"),
        ("ÑUÑOA", "ÑUÑOA"),
        ("VITACURA", "VITACURA"),
        ("LO BARNECHEA", "LO BARNECHEA"),
        ("SAN MIGUEL", "SAN MIGUEL"),
        ("LA FLORIDA", "LA FLORIDA"),
    ]
    
    nombre = models.CharField(max_length=150)
    comuna = models.CharField(max_length=50, choices=Comunas)
    
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return f"{self.nombre} ({self.get_comuna_display()})"