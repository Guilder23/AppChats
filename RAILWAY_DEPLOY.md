# Deploy en Railway

## 1. Preparar GitHub

1. Confirma que `.env` no se suba al repositorio.
2. Haz commit de `Procfile`, `railway.json`, `.env.example` y los cambios de `config/settings.py`.
3. Sube el proyecto a GitHub.

Nunca subas `.env`, contrasenas ni claves reales.

## 2. Crear el proyecto

1. Entra en https://railway.app y crea un proyecto nuevo.
2. Selecciona **Deploy from GitHub Repo**.
3. Elige este repositorio y espera al primer build.

## 3. Crear PostgreSQL

Dentro del proyecto de Railway:

1. Pulsa **Add** y agrega **PostgreSQL**.
2. En el servicio web, abre **Variables**.
3. Agrega `DATABASE_URL` usando la referencia de Railway al PostgreSQL, normalmente seleccionando `Add Reference` y `DATABASE_URL`.

## 4. Crear Redis

1. Pulsa **Add** y agrega Redis.
2. En el servicio web agrega `REDIS_URL` como referencia a la URL de Redis.
3. Esto es necesario para que Channels funcione entre procesos en producción.

## 5. Variables del servicio web

Configura estas variables en **Variables** del servicio Django:

```text
SECRET_KEY=<genera-una-clave-larga-y-aleatoria>
DEBUG=False
ALLOWED_HOSTS=<dominio-publico-de-railway>
RAILWAY_PUBLIC_DOMAIN=<dominio-publico-de-railway>
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

Si Railway muestra otro nombre para los servicios, usa el nombre que aparece en tu proyecto al crear las referencias.

## 6. Dominio

1. Abre el servicio web y entra en **Settings > Networking**.
2. Genera un dominio público `*.up.railway.app` o agrega tu dominio propio.
3. Coloca solamente el hostname, sin `https://`, en `ALLOWED_HOSTS` y `RAILWAY_PUBLIC_DOMAIN`.
4. Reinicia el servicio después de guardar las variables.

## 7. Verificar el despliegue

El proceso de inicio ejecuta automáticamente:

```text
python manage.py migrate --noinput
daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

El build ejecuta `collectstatic`. Revisa los logs del servicio y abre:

```text
https://TU_DOMINIO.up.railway.app/
```

Prueba registro, login, mensajes en tiempo real y notificaciones.

## Archivos subidos

PostgreSQL y los archivos estáticos están preparados. `media/` contiene avatares y adjuntos, pero el disco del contenedor de Railway es efímero: esos archivos pueden desaparecer al redeployar o reiniciar.

Para conservar avatares y adjuntos en producción, agrega un volumen persistente montado en `/app/media` o migra `DEFAULT_FILE_STORAGE` a un servicio S3 compatible antes de usar el sistema en producción.

## Comandos locales útiles

```powershell
pip install -r requirements.txt
python manage.py check
python manage.py collectstatic --noinput
python manage.py migrate
```
