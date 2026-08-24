# La Fiore · carruseles de cuidado en casa + publicación automática

Genera 10 carruseles de 6 láminas (1080×1350, JPG q95) más su historia 9:16 con
la identidad de **La Fiore** y los publica en `@la_fiore.cl` los lunes y los
miércoles, sin que tengas que tocar nada.

La línea editorial es una sola: **enseñar a cuidar el resultado en casa y decir
cuándo toca volver**. De ahí sale la venta cruzada de producto y la reserva de
la próxima hora.

---

## 1. Qué hay en cada carpeta

```
lafiore-salon/
├── assets/
│   ├── logo_dorado.png  logo_blanco.png  logo_negro.png   el sello, con transparencia
│   └── fonts/           LadyIce-Bold.ttf, PlayfairDisplay, Karla y las candidatas
├── plantilla/
│   ├── iconos.py        librería de ilustraciones SVG propias (86 iconos)
│   ├── plantilla.py     HTML/CSS de las láminas
│   ├── preparar_logos.py  reextrae el sello desde el original vectorial
│   └── render.py        render con Chromium + control de calidad
├── contenido/
│   ├── sets.py          el copy de los 10 carruseles
│   └── captions.py      los textos de Instagram
├── salida/
│   ├── set_01/ … set_10/    6 JPG + historia.jpg por carpeta
│   └── captions.json
├── insumos/             material de marca en bruto (no se sube al repo)
├── publicar.py          publica un carrusel + su historia vía Graph API
├── estado.json          qué set se publicó y cuándo
└── .github/workflows/publicar.yml   el cron de lunes y miércoles
```

---

## 2. La identidad

Todo sale de los originales de la marca, que están en `insumos/`.

### Tipografías

Tres papeles, y cada uno tiene su fuente:

| Papel | Tipografía | Dónde |
|---|---|---|
| Marca | **Lady Ice Bold** | solo el sello y el `LA FIORE` de la cabecera |
| Display | **Playfair Display Bold** | titulares, el plazo del cierre y EL DATO |
| Texto | **Karla** | todo lo que se lee de corrido |

Lady Ice es el logotipo y por eso no se usa en más partes: repetida en cada
titular deja de leerse como marca y compite consigo misma. Playfair y Karla
son la dirección editorial que se eligió después de revisar referencias del
rubro, donde el patrón dominante es serif con carácter arriba y sans limpia
abajo. Las tres son de licencia libre y se embeben en base64 dentro de cada
lámina, así que el render no depende de que estén instaladas en el sistema.

Los titulares van en caja normal, no en mayúsculas: una serif de alto
contraste pierde su elegancia en caja alta. Y las cifras están forzadas a
apoyarse en la línea base, porque Playfair trae cifras antiguas por defecto y
el número del plazo (*Cada 3 semanas*) es el mensaje central del cierre.

**Probar otra dirección tipográfica.** Los pares están declarados en
`plantilla/plantilla.py` y se cambian sin tocar el diseño:

```bash
LAFIORE_PAR=instrument python plantilla/render.py 1
```

Pares disponibles: `playfair` (el elegido), `instrument`, `fraunces`,
`bodoni` y `ladyice` (Lady Ice + Akzidenz, el kit original del manual).

### Paleta

De `LA FIORE_Interiorismo V2.pdf`, página 10 — *metal negro y dorado /
ladrillos / cuero / madera*:

| Color | Valor | Dónde va |
|---|---|---|
| Negro | `#15181A` | fondo de portada y de cierre |
| Hueso | `#EDE9D1` | fondo de las láminas interiores |
| Dorado sobre claro | `#90651F` | titulares resaltados, folio, sello del pie |
| Dorado sobre negro | `#E1C58F` | el dorado metálico, aclarado para que contraste |
| Cuero | `#6E432A` | antetítulos y bajadas |
| Blanco | `#FFFFFF` | texto principal sobre negro |

El dorado del interiorismo es un metálico con gradiente, así que no tiene un
solo valor: sobre negro se usa su tono claro y sobre hueso el dorado impreso
del vinilo de acceso, que es el mismo color con contraste suficiente.

### El sello

`plantilla/preparar_logos.py` lo reextrae desde `LA FIORE_Interiorismo V2.pdf`
(página 4) y deja las tres versiones con transparencia real.

**Por qué esa página y no el vinilo de acceso:** en el vinilo, cada letra de
FIORE lleva una sombra desplazada detrás. Al reducir el sello a un solo color,
la letra y su sombra quedan del mismo tono y la palabra se lee doble y sucia a
tamaño pequeño. La versión del interiorismo es de un solo color y trazo limpio.

Solo hace falta correrlo si cambia el original:

```bash
python plantilla/preparar_logos.py
```

---

## 3. Generar las imágenes

Solo la primera vez:

```bash
pip install -r requirements.txt && python -m playwright install chromium
```

Y para renderizar:

```bash
python plantilla/render.py
```

Opciones:

```bash
python plantilla/render.py 1        # solo el set 01
python plantilla/render.py 1 3 7    # sets sueltos
```

Los formatos de salida son los de Instagram: el carrusel en **1080×1350 (4:5)**,
que es el retrato máximo que admite el feed y el que más alto ocupa en pantalla,
y la historia en **1080×1920 (9:16)**.

El render revisa cada lámina por su cuenta: que nada invada el pie, que ningún
texto se salga de su caja, que cada línea de EL DATO quepa en un renglón, que
las ilustraciones no pasen de su columna y que las fuentes hayan cargado de
verdad. Si algo no cabe, lo avisa por pantalla y termina con
error.

**La regla al corregir un desborde es acortar el texto, nunca achicar la
tipografía.** El sistema tipográfico es el de la marca.

---

## 4. Los 10 carruseles

Cada uno cubre un servicio y termina diciendo cada cuánto volver.

| # | Sección | Tema | Plazo |
|---|---|---|---|
| 01 | Manicure | Esmaltado permanente: el retiro tiene fecha | cada 3 semanas |
| 02 | Color | El color se lava, no se destiñe | cada 4 a 6 semanas |
| 03 | Barbería | La barba crece sin forma | cada 2 a 3 semanas |
| 04 | Barbería | El degradado vive tres semanas | cada 3 a 4 semanas |
| 05 | Pedicure | La rutina que evita la grieta | cada 4 a 6 semanas |
| 06 | Cosmetología | La limpieza facial es mantención | cada 4 a 6 semanas |
| 07 | Cabello | El pelo largo se logra con tijera | cada 8 a 12 semanas |
| 08 | Manicure | El relleno sostiene la uña | cada 3 semanas |
| 09 | Cejas y pestañas | La mirada se arma con dos milímetros | cada 3 a 4 semanas |
| 10 | Masajes | La contractura no llegó ayer | cada 3 a 4 semanas |

La estructura de las seis láminas es siempre la misma:

1. **Portada** en negro, con el titular y el sello.
2. a 5. **Cuatro claves**, cada una con `EN CASA` (lo que hace la clienta),
   `EN EL SALÓN` (lo que hacemos nosotros) y `EL DATO` (el porqué, en dos líneas).
6. **Cierre** en negro, con el plazo en grande, los servicios que lo cubren y
   la invitación a agendar.

---

## 5. Publicar en Instagram

### 5.1 Lo que necesitas tener (una sola vez)

**a) `@la_fiore.cl` como cuenta profesional vinculada a una página de Facebook**

1. En Instagram: *Configuración → Cuenta → Cambiar a cuenta profesional*.
2. Crea o elige una página de Facebook y vincúlala:
   *Configuración → Centro de cuentas → Cuentas → Añadir la página*.

Sin este vínculo la API no funciona. Es el paso que más se olvida.

**b) Una app en developers.facebook.com**

1. Entra a <https://developers.facebook.com> con la cuenta de Facebook dueña de
   la página, y haz *Mis apps → Crear app*.
2. Tipo de app: **Empresa (Business)**.
3. Añade el producto **Instagram Graph API**.
4. Permisos: `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
   `business_management`.

**c) El token de 60 días y el `IG_USER_ID`**

Todo se hace en el navegador, sin consola y **sin la clave secreta de la app**.

1. Ve al **Explorador de la API Graph**
   (<https://developers.facebook.com/tools/explorer/>).
2. Arriba a la derecha, elige tu app y pulsa **Generar token de acceso**.
   Marca los cuatro permisos y acepta. Cuando salga la lista de páginas,
   **incluye la página vinculada a @la_fiore.cl**: si solo autorizas la de
   Academy, después no aparece el salón.
3. Copia ese token con el icono de copiar. Dura 1 hora.
4. Ve al **Depurador de tokens de acceso**
   (<https://developers.facebook.com/tools/debug/accesstoken/>), pega el token
   y pulsa **Depurar**.
5. Abajo del todo aparece el botón **«Ampliar token de acceso»**. Púlsalo.
   El token que devuelve es el de 60 días: ese es tu **`IG_ACCESS_TOKEN`**.
6. Vuelve al Explorador, pega el token largo en el campo de arriba y pide:

   ```
   me/accounts?fields=name,instagram_business_account{id,username}
   ```

   En la respuesta busca la página cuyo `username` sea `la_fiore.cl`. El `id`
   que está dentro de su `instagram_business_account` es tu **`IG_USER_ID`**.
   Ojo: es el id de dentro de `instagram_business_account`, no el `id` de la
   página, que es otro número.

> **Por qué así y no por consola.** El intercambio por `curl` con la clave
> secreta de la app es el método que documenta Meta, pero pide distinguir
> entre dos claves parecidas y falla con un error poco claro cuando te
> equivocas. El Depurador hace el mismo intercambio del lado del servidor y
> no necesita la clave. Si aun así prefieres la consola, en el repositorio
> está `obtener_credenciales.py`, que pide clave y token ocultos y hace los
> dos pasos de una vez.

> **Ojo:** `@la_fiore.cl` es una cuenta distinta de `@La_Fiore_Academy`. El
> token y el `IG_USER_ID` de Academy **no sirven aquí**. Hay que sacar los de
> esta cuenta.

**d) Las imágenes en una URL pública**

La API de Meta no acepta archivos: solo URLs que pueda descargar. Lo más simple
es dejar que las sirva el propio repositorio de GitHub. Si el repo es público:

```
https://raw.githubusercontent.com/TU_USUARIO/lafiore-salon/main/salida
```

Comprueba que funciona abriendo `…/salida/set_01/01_portada.jpg` en el
navegador. Si prefieres no tener el repo público, sirve `salida/` desde
Cloudinary, S3 o GitHub Pages y usa esa base.

### 5.2 Los tres secretos

En el repositorio: *Settings → Secrets and variables → Actions → New repository secret*.

| Nombre | Qué va |
|---|---|
| `IG_USER_ID` | el id de la cuenta `@la_fiore.cl` |
| `IG_ACCESS_TOKEN` | el token de 60 días |
| `IG_BASE_URL` | la URL pública de `salida/`, sin barra final |

**Nunca escribas el token dentro de un archivo del repositorio.** Solo en Secrets.

### 5.3 Probar antes de publicar de verdad

```bash
python publicar.py --verificar   # nombre de la cuenta y cuota usada
python publicar.py --dry-run     # qué imágenes y qué caption se enviarían
```

### 5.4 Publicar

```bash
python publicar.py            # el siguiente set pendiente
python publicar.py --set 3    # forzar el set 03
python publicar.py --estado   # ver qué se publicó y qué falta
```

Cada ejecución sube el carrusel de 6 láminas y después la historia 9:16. Si la
historia falla, el carrusel ya publicado no se cae: se registra el aviso y sigue.

---

## 6. El cron

`.github/workflows/publicar.yml` publica **un set los lunes y los miércoles a
las 12:00 de Chile**. Con 10 sets, eso cubre cinco semanas.

Como Chile cambia de hora dos veces al año, el cron se lanza a las 15:00 y a
las 16:00 UTC, y el script comprueba la hora real en Santiago: publica en la
ejecución correcta e ignora la otra. No hay que tocar nada en marzo ni en
septiembre.

Para cambiar los días, edita las dos líneas `cron`: `1,3` son lunes y miércoles
(0 = domingo).

Al terminar, guarda el resultado en `estado.json` y lo sube al repositorio. Si
algo falla, reintenta con esperas crecientes y, si aun así no lo consigue, abre
un **issue** contando qué pasó.

También puedes lanzarlo a mano desde *Actions → Publicar carrusel del día →
Run workflow*.

---

## 7. Mantención

### Renovar el token antes de los 60 días

Ponte un recordatorio para el día 50:

```bash
curl -s "https://graph.facebook.com/v26.0/oauth/access_token?grant_type=fb_exchange_token&client_id=TU_APP_ID&client_secret=TU_APP_SECRET&fb_exchange_token=EL_TOKEN_ACTUAL"
```

Pega el nuevo valor en el secreto `IG_ACCESS_TOKEN`.

### Cambiar o añadir contenido

El copy está en `contenido/sets.py` y los textos de Instagram en
`contenido/captions.py`. Reglas que el propio código verifica:

- La palabra **«oficio» está prohibida**.
- `EN CASA` y `EN EL SALÓN`: máximo 52 caracteres.
- Cada línea de `EL DATO`: máximo 34 caracteres.
- Titular de portada: máximo 78 caracteres.
- El icono citado tiene que existir en `plantilla/iconos.py`.

Y la regla que no verifica ningún programa, pero manda: **nunca se corrige ni
se reta a quien lee.** `EN CASA` es una indicación, no un reproche. El carrusel
enseña a cuidar el resultado; no señala lo que la clienta hizo mal.

Los servicios que se nombran salen del catálogo real del salón
(`insumos/services_report_*.xlsx`, 193 servicios en 17 categorías). Si cambian
los precios o los nombres, hay que revisar las láminas de cierre.

Después de editar, vuelve a renderizar y sube los JPG:

```bash
python plantilla/render.py
```

### Límites de Meta

- Máximo **25 publicaciones por API cada 24 horas**. Publicando dos por semana,
  sobra de lejos; el script igual consulta la cuota antes de subir.
- Un contenedor de carrusel caduca a las 24 horas si no se publica.
- Máximo 10 imágenes por carrusel (aquí van 6).
