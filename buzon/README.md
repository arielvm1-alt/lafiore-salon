# Buzón de réplica automática a TikTok

Lo que caiga en la carpeta **«Buzon TikTok» de Google Drive** se envía solo
como borrador al buzón de TikTok de `@la_fiore.cl`. Da lo mismo desde dónde
se suba: el teléfono (app de Drive), el computador o una automatización de
Claude Code. Cada 20 minutos un workflow revisa la carpeta, publica los
archivos en el sitio verificado y hace el envío en modo `MEDIA_UPLOAD`;
la notificación llega a la app de TikTok y ahí se publica de un toque.

## Cómo se usa (día a día)

1. En Drive, dentro de «Buzon TikTok», crea **una carpeta por publicación**
   (el nombre que quieras: «Corte fade viernes», «Promo alisado»…).
2. Mete adentro el material:
   - **2 o más imágenes** → carrusel de fotos (orden alfabético de archivo:
     `01.jpg`, `02.jpg`… si te importa el orden).
   - **1 imagen** → foto suelta; sirve para historia, el formato se elige al
     publicar desde el teléfono.
   - **un `.mp4`** → video (menos de 95 MB). Si además hay imágenes, se
     ignoran.
   - **`texto.txt`** (opcional) → el copy del post. Sin él, se usa el nombre
     de la carpeta. Los borradores de **video** no aceptan texto por API: el
     copy se escribe al publicar.
3. Espera. Cuando la carpeta lleve ~10 minutos sin cambios, la siguiente
   pasada la envía. Aparece **«ENVIADO A TIKTOK.txt»** dentro de la carpeta
   de Drive como confirmación, y la notificación en la app de TikTok.
4. Abre la notificación en TikTok, elige música/formato y publica.

Reglas:
- **Una carpeta se envía una sola vez.** Si después le agregas archivos, se
  ignoran: para otro post, otra carpeta.
- No borres la carpeta de Drive antes de ver la marca de enviado.
- También funciona sin Drive: deja la carpeta directamente en
  `buzon/entrada/` del repo y haz push — el envío sale al momento.
- **Ojo:** los archivos quedan servidos en el sitio público del repo
  (`…github.io/lafiore-salon/buzon/…`). No subas nada que no pueda ser
  público.

## Puesta en marcha (una sola vez)

Los secretos `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` y
`TIKTOK_REFRESH_TOKEN` son los mismos del publicador de sets (README
principal, sección de TikTok). Lo único nuevo es darle acceso a Drive:

1. Crea en tu Google Drive la carpeta **`Buzon TikTok`** (así, sin acento).
2. En el computador, instala [rclone](https://rclone.org/downloads/) y corre:

   ```
   rclone config
   ```

   `n` (nuevo) → nombre **`gdrive`** → tipo **`drive`** → client id y secret
   en blanco → scope **`1`** (acceso completo) → resto por defecto → se abre
   el navegador para autorizar con la cuenta del Drive.
3. Muestra la configuración y cópiala completa:

   ```
   rclone config show gdrive
   ```

4. En GitHub: repo `lafiore-salon` → Settings → Secrets and variables →
   Actions → **New repository secret** → nombre `RCLONE_CONF`, valor = lo
   que copiaste (incluida la línea `[gdrive]`).
5. Prueba: sube una carpeta con dos fotos a «Buzon TikTok» y lanza a mano el
   workflow **Buzon TikTok** (pestaña Actions → Run workflow), o espera la
   pasada de los 20 minutos.

Sin el secreto `RCLONE_CONF`, el workflow no falla: simplemente procesa solo
lo que llegue por git a `buzon/entrada/`.

## Piezas

- `publicar_buzon.py` — clasifica cada carpeta (carrusel / foto / video),
  renombra a nombres seguros de URL, espera a que GitHub Pages sirva los
  archivos y llama a la Content Posting API. `--estado` muestra el
  historial; `--dry-run` ensaya sin llamar a la API.
- `estado_buzon.json` — qué se envió, cuándo y con qué `publish_id`.
- `.github/workflows/buzon-tiktok.yml` — la pasada cada 20 minutos
  (Drive → repo → Pages → TikTok → marca en Drive).
- Las trampas de TikTok (URL verificada, Sandbox, MEDIA_UPLOAD) están
  explicadas en el README principal; aquí solo se reutiliza lo que ya
  funciona.
