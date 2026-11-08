from django.db import models

class areasverdes(models.Model):
    Comunas = [
        ("ALHUÉ", "ALHUÉ"),
        ("BUIN", "BUIN"),
        ("CALERA DE TANGO", "CALERA DE TANGO"),
        ("CERRILLOS", "CERRILLOS"),
        ("CERRO NAVIA", "CERRO NAVIA"),
        ("COLINA", "COLINA"),
        ("CONCHALÍ", "CONCHALÍ"),
        ("CURACAVÍ", "CURACAVÍ"),
        ("EL BOSQUE", "EL BOSQUE"),
        ("EL MONTE", "EL MONTE"),
        ("ESTACIÓN CENTRAL", "ESTACIÓN CENTRAL"),
        ("HUECHURABA", "HUECHURABA"),
        ("INDEPENDENCIA", "INDEPENDENCIA"),
        ("ISLA DE MAIPO", "ISLA DE MAIPO"),
        ("LA CISTERNA", "LA CISTERNA"),
        ("LA FLORIDA", "LA FLORIDA"),
        ("LA GRANJA", "LA GRANJA"),
        ("LA PINTANA", "LA PINTANA"),
        ("LA REINA", "LA REINA"),
        ("LAMPA", "LAMPA"),
        ("LAS CONDES", "LAS CONDES"),
        ("LO BARNECHEA", "LO BARNECHEA"),
        ("LO ESPEJO", "LO ESPEJO"),
        ("LO PRADO", "LO PRADO"),
        ("MACUL", "MACUL"),
        ("MAIPÚ", "MAIPÚ"),
        ("MARÍA PINTO", "MARÍA PINTO"),
        ("MELIPILLA", "MELIPILLA"),
        ("ÑUÑOA", "ÑUÑOA"),
        ("PADRE HURTADO", "PADRE HURTADO"),
        ("PAINE", "PAINE"),
        ("PEDRO AGUIRRE CERDA", "PEDRO AGUIRRE CERDA"),
        ("PEÑAFLOR", "PEÑAFLOR"),
        ("PEÑALOLÉN", "PEÑALOLÉN"),
        ("PIRQUE", "PIRQUE"),
        ("PROVIDENCIA", "PROVIDENCIA"),
        ("PUDAHUEL", "PUDAHUEL"),
        ("PUENTE ALTO", "PUENTE ALTO"),
        ("QUILICURA", "QUILICURA"),
        ("QUINTA NORMAL", "QUINTA NORMAL"),
        ("RECOLETA", "RECOLETA"),
        ("RENCA", "RENCA"),
        ("SAN BERNARDO", "SAN BERNARDO"),
        ("SAN JOAQUÍN", "SAN JOAQUÍN"),
        ("SAN JOSÉ DE MAIPO", "SAN JOSÉ DE MAIPO"),
        ("SAN MIGUEL", "SAN MIGUEL"),
        ("SAN PEDRO", "SAN PEDRO"),
        ("SAN RAMÓN", "SAN RAMÓN"),
        ("SANTIAGO", "SANTIAGO CENTRO"),
        ("TALAGANTE", "TALAGANTE"),
        ("TILTIL", "TILTIL"),
        ("VITACURA", "VITACURA"),
    ]
    
    nombre = models.CharField(max_length=150)
    comuna = models.CharField(max_length=50, choices=Comunas)
    
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return f"{self.nombre} ({self.get_comuna_display()})"