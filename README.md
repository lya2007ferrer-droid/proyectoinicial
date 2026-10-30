# Áreas Verdes en Santiago
Dependencias:
- Python 3.X
- Django 6.1.2
- Leaflet.js y Esri Tile Layers

Ejecución entorno local:
1. Clonar el repositorio y dirigirse a la raíz del proyecto.
2. Crear entorno virtual: python -m venv venv
3. Activar entorno virtual: .\venv\Scripts\activate (Windows) o source venv/bin/activate (Mac/Linux)
4. Instalar Django: pip install django
5. Aplicar las migraciones para iniciar la base de datos SQLite: python manage.py migrate
6. Inicia el servidor de desarrollo: python manage.py runserver
7. Abre en tu navegador: http://127.0.0.1:8000/
