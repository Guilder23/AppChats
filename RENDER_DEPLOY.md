# Deploy en Render

El archivo `render.yaml` crea el servicio web Django, PostgreSQL y Redis. El servicio web usa Daphne porque el proyecto tiene WebSockets con Django Channels.

## 1. Subir el proyecto a GitHub

```powershell
git add .
git commit -m "Preparar deploy en Render"
git push origin main
```

No subas `.env`, contrasenas ni claves reales.

## 2. Crear el servicio desde Blueprint

1. Entra en https://dashboard.render.com.
2. Selecciona **New > Blueprint**.
3. Conecta el repositorio de GitHub.
4. Selecciona la rama `main`.
5. Render detectara `render.yaml` y mostrara un servicio web, PostgreSQL y Redis.
6. Confirma **Apply**.

El build ejecuta `bash build.sh`, que instala las dependencias y ejecuta `collectstatic`. El arranque ejecuta migraciones y Daphne:

```text
python manage.py migrate --noinput && daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

## 3. Variables de entorno

El Blueprint configura automaticamente:

- `SECRET_KEY`: generada por Render.
- `DEBUG=False`.
- `DATABASE_URL`: referencia al PostgreSQL creado.
- `REDIS_URL`: referencia al Redis creado.
- `ALLOWED_HOSTS=.onrender.com`.
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`.

Si agregas un dominio propio, anade su hostname a `ALLOWED_HOSTS` y su URL completa, con `https://`, a `CSRF_TRUSTED_ORIGINS`.

## 4. Probar la aplicación

Cuando termine el deploy, abre el dominio que aparece en **Settings > Domains** y verifica:

1. Registro e inicio de sesion.
2. Creacion de conversaciones.
3. Mensajes en tiempo real en dos navegadores.
4. Notificaciones de mensajes.
5. Avatares y adjuntos.

## 5. Crear un administrador

Render no ejecuta comandos de administrador automaticamente. En el servicio web abre **Shell** y ejecuta:

```bash
python manage.py createsuperuser
```

## Archivos media

Los archivos de `media/` no deben depender del disco efimero del servicio. Para conservar avatares y adjuntos después de reinicios o deploys, configura un disco persistente de Render montado en `/app/media` o usa almacenamiento compatible con S3.

## Diagnostico rapido

- Si falla el build, revisa **Logs** y confirma que `requirements.txt` esta en la raiz.
- Si aparece `DisallowedHost`, agrega el dominio real a `ALLOWED_HOSTS`.
- Si falla CSRF, agrega `https://tu-dominio` a `CSRF_TRUSTED_ORIGINS`.
- Si los mensajes no llegan en tiempo real, confirma que `REDIS_URL` esta conectado al servicio Redis.