import csv
import json
import time
import unicodedata

from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand
from myapp.models import areasverdes


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto or "")
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    return texto.casefold().strip()


class Command(BaseCommand):
    help = "Busca posibles contornos de parques en OpenStreetMap"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limite", type=int, default=3
        )

    def handle(self, *args, **options):
        parques = areasverdes.objects.filter(
            contorno_geojson__isnull=True
        ).order_by("id")

        limite = options["limite"]
        if limite > 0:
            parques = parques[:limite]

        carpeta = Path("myapp/datos_geograficos")
        carpeta.mkdir(parents=True, exist_ok=True)

        archivo = carpeta / "candidatos_contornos.csv"

        with archivo.open(
            "w", newline="", encoding="utf-8-sig"
        ) as f:

            escritor = csv.writer(f)
            escritor.writerow([
                "ID parque", "Parque", "Comuna",
                "Candidato OSM", "Similitud", "Enlace OSM"
            ])

            for parque in parques:
                self.stdout.write(
                    f"\nBuscando: {parque.nombre}"
                )

                if parque.latitud is None or parque.longitud is None:
                    self.stdout.write("Sin coordenadas")
                    continue

                lat = float(parque.latitud)
                lon = float(parque.longitud)

                consulta = f"""
                [out:json][timeout:30];
                (
                  way(around:650,{lat},{lon})
                    ["leisure"~"^(park|garden|recreation_ground)$"];
                  relation(around:650,{lat},{lon})
                    ["leisure"~"^(park|garden|recreation_ground)$"];
                  way(around:650,{lat},{lon})
                    ["landuse"="recreation_ground"]["name"];
                );
                out center;
                """

                try:
                    peticion = Request(
                        "https://overpass-api.de/api/interpreter",
                        data=urlencode(
                            {"data": consulta}
                        ).encode("utf-8"),
                        headers={
                            "User-Agent": "GeoVerde-educational/1.0"
                        }
                    )

                    with urlopen(peticion, timeout=60) as respuesta:
                        datos = json.load(respuesta)

                except Exception as error:
                    self.stdout.write(
                        f"Consulta fallida: {error}"
                    )
                    continue

                candidatos = []

                for elemento in datos.get("elements", []):
                    etiquetas = elemento.get("tags", {})
                    nombre = (
                        etiquetas.get("name")
                        or etiquetas.get("name:es")
                        or etiquetas.get("official_name")
                    )

                    if not nombre:
                        continue

                    similitud = SequenceMatcher(
                        None,
                        normalizar(parque.nombre),
                        normalizar(nombre)
                    ).ratio()

                    enlace = (
                        f"https://www.openstreetmap.org/"
                        f"{elemento['type']}/{elemento['id']}"
                    )

                    candidatos.append(
                        (similitud, nombre, enlace)
                    )

                candidatos.sort(reverse=True)

                if not candidatos:
                    self.stdout.write(
                        "No se encontraron candidatos"
                    )

                for similitud, nombre, enlace in candidatos[:3]:
                    escritor.writerow([
                        parque.id,
                        parque.nombre,
                        parque.comuna,
                        nombre,
                        round(similitud, 2),
                        enlace
                    ])

                    self.stdout.write(
                        f"  {nombre} "
                        f"(similitud: {similitud:.2f})"
                    )

                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nReporte creado: {archivo}"
            )
        )
