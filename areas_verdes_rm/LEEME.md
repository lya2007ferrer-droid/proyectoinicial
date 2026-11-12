# Áreas verdes de la Región Metropolitana: CSV por comuna

Preparado el 12 de noviembre de 2026 para el proyecto Django «Áreas verdes en Santiago».

## Contenido y cobertura

- `comunas/`: 52 archivos CSV separados, uno por comuna de la Región Metropolitana.
- 8.416 registros geográficos: 612 clasificados como PARQUE y 7.804 como PLAZA.
- 49 comunas con registros. Los CSV de Curacaví, María Pinto y San Pedro contienen solo la cabecera: no se obtuvieron registros para ellas en las dos fuentes descargadas. Esto NO significa que carezcan de áreas verdes.
- `resumen_comunas.csv`: cantidad de registros, parques, plazas, nombres provisionales y fuente por comuna.
- `metadatos/registros_fuente.json`: identificadores y atributos originales para revisar cada registro.
- `django/myapp/management/commands/importar_areas_verdes.py`: comando opcional para importar los CSV al modelo `areasverdes`.

Este paquete NO es un inventario exhaustivo ni una verificación en terreno de todas las áreas verdes existentes en 2026. Su cobertura es la de las fuentes consultadas; pueden faltar lugares o existir registros que requieran actualización. Un registro representa un polígono de origen y no necesariamente un parque físico único: algunos parques tienen varios sectores o se reparten entre comunas.

## Fuentes

1. **MINVU/INE, servicio «Áreas_Verdes_MINVU_INE_2023»**: 8.160 registros de la Región Metropolitana, descargados con filtro CUT entre 13000 y 13999. Etiqueta `MINVU_INE_2023`.
   - Catálogo: https://ide.minvu.cl/datasets/MINVU%3A%3Aareas-verdes-minvu-ine/about
   - Servicio: https://geoide.minvu.cl/server/rest/services/Catastros/%C3%81reas_Verdes_MINVU_INE_2023/FeatureServer/0
   - El nombre del servicio hace referencia a 2023; la fecha de consulta no implica que cada registro esté actualizado a 2026.
2. **MINVU/INE-SIEDU, capa «Catastro Parques» del servicio «Catastro_areas_verdes»**, con última edición de datos informada por el servicio el 26-06-2020: 256 registros adicionales, únicamente para cinco comunas ausentes en la primera descarga. Etiqueta `MINVU_INE_SIEDU_2020`.
   - Servicio: https://services3.arcgis.com/cTnMkBRk4HWkUCRo/ArcGIS/rest/services/Catastro_areas_verdes/FeatureServer/0
   - Tiltil: 36; Calera de Tango: 18; Paine: 87; El Monte: 71; Isla de Maipo: 44.

Crédito de los datos: MINVU e INE/SIEDU, según los servicios indicados. Conversión a puntos y separación por comuna realizadas para este proyecto. Conservar esta atribución y consultar las condiciones de reutilización de los catálogos originales antes de redistribuir los datos.

## Columnas y formato

| Columna | Descripción |
|---|---|
| nombre | Texto para el campo `nombre` de tu modelo. |
| comuna | Valor en mayúsculas compatible con la lista de las 52 comunas compartida en la conversación. Para Tiltil se utiliza `TILTIL`. |
| latitud | Grados decimales WGS84, EPSG:4326. |
| longitud | Grados decimales WGS84, EPSG:4326. |
| id_fuente | Identificador del registro y su capa de origen. |
| tipo | PARQUE o PLAZA, según la clasificación original. |
| nombre_original | Valor original de NOMBRE_EP; puede estar vacío o ser un código sin nombre identificable. |
| fuente | Identifica la fuente y permite distinguir la capa 2023 de la complementaria con última edición 2020. |

Codificación UTF-8 con BOM para conservar tildes y la Ñ; delimitador coma; separador decimal punto. El comando incluido usa `utf-8-sig` y admite la cabecera BOM.

Los nombres originales se conservan. En 3.177 registros sin un nombre identificable (vacíos, «SIN NOMBRE», genéricos o solo numéricos), el campo `nombre` utiliza una etiqueta provisional como `Plaza sin nombre (MINVU-1234)`. Esa etiqueta NO es un nombre oficial; el original queda en `nombre_original`. Reemplazarla al verificar el lugar.

Las coordenadas fueron calculadas como un **punto interior** del componente de mayor superficie del polígono de origen. Se validó que cada punto estuviera dentro de su polígono y en el rango geográfico de la RM. No representan necesariamente un acceso ni un punto para navegación vehicular. Un marcador no reproduce la forma o extensión de un parque.

No se agregaron actividades, horarios, precios, accesibilidad ni reseñas: las fuentes descargadas no permiten confirmar esos datos para todos los lugares. Las actividades se pueden completar después desde tu administrador.

## Importar al proyecto Django

1. Extrae el ZIP y deja la carpeta `areas_verdes_rm` dentro de la carpeta de tu proyecto donde está `manage.py`.
2. Copia la carpeta `areas_verdes_rm/django/myapp/management` dentro de tu carpeta `myapp`. Si ya tienes `management`, incorpora únicamente el comando y conserva tus otros archivos.
3. Mantén los archivos `__init__.py` incluidos en `management` y `commands`.
4. Comprueba que tu modelo se llama `areasverdes`, tiene los campos `nombre`, `comuna`, `latitud` y `longitud`, y sus choices contienen las 52 comunas. El comando normaliza tildes y espacios al comparar las comunas, por lo que también admite `TIL TIL` si tu modelo utiliza esa variante.
5. Guarda una copia de `db.sqlite3` con el servidor detenido antes de la primera importación.
6. Desde la terminal, dentro de la carpeta de `manage.py`, con tu entorno virtual activado:

```bash
python manage.py check
python manage.py migrate
```

Primero valida todos los archivos sin guardar datos:

```bash
python manage.py importar_areas_verdes areas_verdes_rm/comunas --simular
```

Si la simulación termina correctamente, importa:

```bash
python manage.py importar_areas_verdes areas_verdes_rm/comunas
```

También puedes cargar solo una comuna:

```bash
python manage.py importar_areas_verdes areas_verdes_rm/comunas/nunoa.csv
```

El comando utiliza los cuatro campos actuales de tu modelo y no requiere agregar `id_fuente`, `tipo` o `fuente` a la base de datos. Las demás columnas se conservan en los CSV para revisión. No borra parques ni modifica las actividades existentes. Los parques nuevos quedan sin actividades asignadas.

La repetición del mismo archivo no vuelve a crear filas con idénticos nombre, comuna, latitud y longitud. Sí puede crear un segundo registro para un parque ingresado manualmente con un nombre diferente o coordenadas distintas: revisar esos casos antes de importar. No se intenta unir lugares solo por nombre, porque pueden existir varias plazas con el mismo nombre en una comuna.

El comando valida todos los CSV antes de escribir y guarda la carga en una transacción. Se comprobó su sintaxis; la ejecución real debe validarse en tu entorno Django mediante `--simular`.

Por último, inicia el servidor y revisa los resultados por comuna:

```bash
python manage.py runserver
```

El selector del mapa debe recibir las comunas desde `mapa_principal`, como se explicó en la conversación. El CSV por sí solo no se incorpora automáticamente a Django.
