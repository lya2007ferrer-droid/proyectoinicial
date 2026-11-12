import csv
import re
import ssl
import time
import unicodedata
import xml.etree.ElementTree as ET

from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

import certifi
from django.core.management.base import BaseCommand
from myapp.models import areasverdes


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(
        c for c in texto if not unicodedata.combining(c)
    ).casefold().strip()


class Command(BaseCommand):
    help = "Importa contornos OSM con nombre y ubicación comprobados"

    def handle(self, *args, **options):
        ruta = Path("myapp/datos_geograficos/candidatos_contornos.csv")

        with ruta.open(encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.DictReader(archivo))

        candidatos = defaultdict(dict)

        for fila in filas:
            similitud = float(fila["Similitud"].replace(",", "."))

            if similitud < 0.9999:
                continue

            parque_id = int(fila["ID parque"])
            enlace = fila["Enlace OSM"].strip()
            candidatos[parque_id][enlace] = fila

        contexto = ssl.create_default_context(
            cafile=certifi.where()
        )

        guardados = 0
        pendientes = 0

        for parque_id, opciones in candidatos.items():
            try:
                parque = areasverdes.objects.get(pk=parque_id)

                if parque.contorno_geojson:
                    continue

                if len(opciones) != 1:
                    raise ValueError("Varios candidatos: revisar manualmente")

                fila = next(iter(opciones.values()))

                if normalizar(fila["Candidato OSM"]) != normalizar(parque.nombre):
                    raise ValueError("El nombre del candidato no coincide")

                enlace = fila["Enlace OSM"]
                coincidencia = re.search(r"/way/(\d+)", enlace)

                if not coincidencia:
                    raise ValueError("No es una vía OSM compatible")

                way_id = coincidencia.group(1)
                url = f"https://api.openstreetmap.org/api/0.6/way/{way_id}/full"

                peticion = Request(
                    url,
                    headers={"User-Agent": "GeoVerde-ProyectoAcademico/1.0"}
                )

                with urlopen(
                    peticion, context=contexto, timeout=25
                ) as respuesta:
                    raiz = ET.fromstring(respuesta.read())

                via = raiz.find(f".//way[@id='{way_id}']")

                if via is None:
                    raise ValueError("No se encontró el polígono")

                etiquetas = {
                    t.get("k"): t.get("v")
                    for t in via.findall("tag")
                }

                if normalizar(etiquetas.get("name")) != normalizar(parque.nombre):
                    raise ValueError("Nombre OSM diferente")

                nodos = {
                    n.get("id"): [
                        float(n.get("lon")),
                        float(n.get("lat"))
                    ]
                    for n in raiz.findall("node")
                }

                referencias = [
                    n.get("ref") for n in via.findall("nd")
                ]

                if (
                    len(referencias) < 4
                    or referencias[0] != referencias[-1]
                ):
                    raise ValueError("El polígono no está cerrado")

                coordenadas = [
                    nodos[ref] for ref in referencias
                ]

                longitudes = [p[0] for p in coordenadas]
                latitudes = [p[1] for p in coordenadas]

                min_lon, max_lon = min(longitudes), max(longitudes)
                min_lat, max_lat = min(latitudes), max(latitudes)

                if (
                    max_lon - min_lon > 0.03
                    or max_lat - min_lat > 0.03
                ):
                    raise ValueError("Contorno demasiado grande: revisar")

                # Comprobar que el parque esté cerca de su polígono.
                margen_lat = 0.003
                margen_lon = 0.0035

                if not (
                    min_lat - margen_lat <= parque.latitud <= max_lat + margen_lat
                    and min_lon - margen_lon <= parque.longitud <= max_lon + margen_lon
                ):
                    raise ValueError("El contorno está lejos del marcador")

                parque.contorno_geojson = {
                    "type": "Polygon",
                    "coordinates": [coordenadas]
                }

                parque.save(update_fields=["contorno_geojson"])

                guardados += 1
                self.stdout.write(
                    f"OK: {parque.nombre} ({len(coordenadas)} puntos)"
                )

            except Exception as error:
                pendientes += 1
                self.stdout.write(
                    f"REVISAR ID {parque_id}: {error}"
                )

            time.sleep(0.5)

        total = areasverdes.objects.count()
        con_contorno = areasverdes.objects.exclude(
            contorno_geojson__isnull=True
        ).exclude(contorno_geojson={}).count()

        self.stdout.write("\n--- RESULTADO ---")
        self.stdout.write(f"Contornos nuevos: {guardados}")
        self.stdout.write(f"Candidatos pendientes de revisión: {pendientes}")
        self.stdout.write(f"Parques con contorno: {con_contorno} de {total}")
