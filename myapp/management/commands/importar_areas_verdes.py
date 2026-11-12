import csv
import math
import unicodedata
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from myapp.models import areasverdes


def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto.upper().strip())
    return ''.join(letra for letra in texto if unicodedata.category(letra) != 'Mn').replace(' ', '')


class Command(BaseCommand):
    help = 'Importa uno o varios CSV de áreas verdes sin borrar datos existentes.'

    def add_arguments(self, parser):
        parser.add_argument('ruta', help='Archivo CSV o carpeta comunas con los 52 CSV.')
        parser.add_argument('--simular', action='store_true', help='Valida y cuenta sin guardar registros.')

    def handle(self, *args, **options):
        ruta = Path(options['ruta'])
        archivos = sorted(ruta.glob('*.csv')) if ruta.is_dir() else [ruta]
        if not archivos or any(not archivo.is_file() for archivo in archivos):
            raise CommandError('No se encontraron archivos CSV válidos en la ruta indicada.')

        opciones = dict(areasverdes._meta.get_field('comuna').choices)
        comunas = {normalizar(valor): valor for valor in opciones}
        max_nombre = areasverdes._meta.get_field('nombre').max_length
        registros = []
        vistos = set()
        repetidos_csv = 0
        for archivo in archivos:
            try:
                with archivo.open(encoding='utf-8-sig', newline='') as entrada:
                    lector = csv.DictReader(entrada)
                    if not {'nombre', 'comuna', 'latitud', 'longitud'}.issubset(lector.fieldnames or []):
                        raise CommandError(f'{archivo.name}: faltan las columnas requeridas.')
                    for numero, fila in enumerate(lector, start=2):
                        nombre = fila['nombre'].strip()
                        tipo = fila.get('tipo', '').strip().upper()
                        nombre_comparado = normalizar(nombre)

                        if tipo == 'PLAZA' and not nombre_comparado.startswith(('PLAZA', 'PLAZOLETA', 'PLAZUELA')):
                            nombre = 'Plaza ' + nombre
                        elif tipo == 'PARQUE' and not nombre_comparado.startswith('PARQUE'):
                            nombre = 'Parque ' + nombre                
                        comuna = comunas.get(normalizar(fila['comuna']))
                        try:
                            latitud = float(fila['latitud'])
                            longitud = float(fila['longitud'])
                        except (TypeError, ValueError) as error:
                            raise CommandError(f'{archivo.name}, fila {numero}: coordenadas inválidas.') from error
                        if not nombre or len(nombre) > max_nombre or comuna is None:
                            raise CommandError(f'{archivo.name}, fila {numero}: revisa el nombre o agrega la comuna a models.py.')
                        if not (math.isfinite(latitud) and math.isfinite(longitud) and -35 < latitud < -32 and -72 < longitud < -69):
                            raise CommandError(f'{archivo.name}, fila {numero}: coordenadas fuera de la Región Metropolitana.')
                        clave = (nombre, comuna, latitud, longitud)
                        if clave in vistos:
                            repetidos_csv += 1
                            continue
                        vistos.add(clave)
                        registros.append(dict(nombre=nombre, comuna=comuna, latitud=latitud, longitud=longitud))
            except (OSError, UnicodeError, csv.Error) as error:
                raise CommandError(f'No se pudo leer {archivo.name}: {error}') from error

        creados = existentes = 0
        with transaction.atomic():
            for registro in registros:
                if areasverdes.objects.filter(**registro).exists():
                    existentes += 1
                else:
                    if not options['simular']:
                        areasverdes.objects.create(**registro)
                    creados += 1

        accion = 'Por crear' if options['simular'] else 'Creados'
        self.stdout.write(self.style.SUCCESS(
            f'Archivos: {len(archivos)} | {accion}: {creados} | Ya existentes: {existentes} | Repetidos en CSV: {repetidos_csv}'
        ))
        if options['simular']:
            self.stdout.write('Simulación terminada: no se guardaron cambios.')
