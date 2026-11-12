# GeoVerde — cómo agregar contornos en el futuro

1. Crear el parque en el administrador Django, con nombre, comuna, latitud y longitud correctos.
2. Buscar geometrías candidatas de OpenStreetMap con:
   `SSL_CERT_FILE="$(python -m certifi)" python manage.py buscar_contornos --limite 0`
3. Revisar en el archivo `candidatos_contornos.csv` las opciones: el nombre similar **no basta**. Comprobar localidad, etiqueta geográfica, polígono completo y ubicación del marcador. Algunos parques carecen de contorno OSM.
4. Consultar `python manage.py importar_contornos --help` antes de importar; usar solamente una geometría confirmada. No importar masivamente candidatos sin revisar.
5. Confirmar visualmente la geometría en GeoVerde: al seleccionar un marcador se debe ver la figura correcta; al cerrar, debe desaparecer.
6. Generar el respaldo: `python manage.py dumpdata myapp.Actividad myapp.areasverdes --indent 2 --output=myapp/fixtures/parques.json`.
7. Compartir las fotos en `media/parques/` por separado: la carpeta `media/` no se sube a GitHub.

**Nota:** el contorno de Cerro Chena representa el *Sitio Prioritario de la Estrategia Regional de Biodiversidad* (Ministerio del Medio Ambiente), no necesariamente el parque metropolitano ni el cerro completo. Las geometrías no se generan automáticamente para cada registro nuevo: requieren una fuente fiable y verificación.
