# -*- coding: utf-8 -*-
"""
Render de las laminas con Chromium (Playwright) + control de calidad.

Uso:
    python plantilla/render.py            # renderiza los 10 sets
    python plantilla/render.py 1          # solo el set 01
    python plantilla/render.py 1 3 7      # sets sueltos

Salida: salida/set_NN/01_portada.jpg ... 06_cierre.jpg  (1080x1350, feed)
        salida/set_NN/historia.jpg                      (1080x1920, historia)
        salida/set_NN/tiktok/01.jpg ... 06.jpg          (1080x1920, TikTok)
        salida/captions.json

La regla al corregir un desborde es acortar el texto, nunca achicar la
tipografia: el sistema tipografico es el de la marca.
"""

import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "contenido"))

from PIL import Image
from playwright.sync_api import sync_playwright

import plantilla
import sets as contenido
import captions as textos_caption

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "salida")

# La consola de Windows usa cp1252 y rompe con emojis y tildes: forzamos UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


ESCALA = 2          # se renderiza a 2x y se reduce -> bordes mas limpios
CALIDAD = 95


# --------------------------------------------------------------------------
# control de calidad dentro de la pagina
# --------------------------------------------------------------------------

QC_JS = r"""
() => {
  const problemas = [];
  const lamina = document.querySelector('.lamina');
  const caja = lamina.getBoundingClientRect();

  // 1. la lamina no debe tener scroll (contenido fuera del lienzo)
  if (lamina.scrollHeight > lamina.clientHeight + 1)
    problemas.push(`la lamina desborda en alto: ${lamina.scrollHeight} > ${lamina.clientHeight}`);
  if (lamina.scrollWidth > lamina.clientWidth + 1)
    problemas.push(`la lamina desborda en ancho: ${lamina.scrollWidth} > ${lamina.clientWidth}`);

  // 2. nada puede invadir el pie
  const pie = document.querySelector('.pie');
  if (pie) {
    const topePie = pie.getBoundingClientRect().top;
    for (const sel of ['.filas', '.titulo', '.antetitulo', '.dato-bloque']) {
      const el = document.querySelector(sel);
      if (!el) continue;
      const b = el.getBoundingClientRect().bottom;
      if (b > topePie + 1)
        problemas.push(`${sel} invade el pie por ${(b - topePie).toFixed(1)}px`);
    }
  }

  // 3. ningun texto puede salirse de su caja ni de la lamina
  const textos = document.querySelectorAll(
    '.cuerpo, .dato-lineas > div, .titulo, .antetitulo, .portada-titulo, .portada-sub, ' +
    '.cierre-plazo, .cierre-detalle, .banda-cta .txt, .banda-cta .sub, ' +
    '.masthead .marca, .masthead .bajada, .etiqueta, .kicker, .pie-txt, .pie-der, ' +
    '.riel span, .cifra');
  for (const el of textos) {
    if (el.scrollWidth > el.clientWidth + 1)
      problemas.push(`texto desbordado (${el.className || el.tagName}): "${el.textContent.trim().slice(0, 40)}"`);
    const r = el.getBoundingClientRect();
    if (r.right > caja.right + 1 || r.left < caja.left - 1 || r.bottom > caja.bottom + 1)
      problemas.push(`texto fuera de lamina: "${el.textContent.trim().slice(0, 40)}"`);
  }

  // 4. cada linea de EL DATO debe caber en un solo renglon
  for (const el of document.querySelectorAll('.dato-lineas > div')) {
    const lh = parseFloat(getComputedStyle(el).lineHeight);
    if (el.offsetHeight > lh * 1.5)
      problemas.push(`dato partido en dos renglones: "${el.textContent.trim()}"`);
  }

  // 5. el plazo del cierre tiene que caber en dos renglones como maximo
  const plazo = document.querySelector('.cierre-plazo');
  if (plazo) {
    const lh = parseFloat(getComputedStyle(plazo).lineHeight);
    if (plazo.offsetHeight > lh * 2.2)
      problemas.push(`el plazo ocupa mas de dos renglones: "${plazo.textContent.trim()}"`);
  }

  // 6. las ilustraciones deben caber en su columna
  for (const el of document.querySelectorAll('.ilu-col')) {
    if (el.getBoundingClientRect().height > 151)
      problemas.push('ilustracion mas alta que 150px');
  }

  // 7. las fuentes de la marca tienen que haber cargado de verdad
  if (!document.fonts.check("700 100px 'Display'"))
    problemas.push('no cargo la fuente de titulares');
  // Lady Ice solo se usa en el masthead: se comprueba donde hay masthead
  if (document.querySelector('.masthead') && !document.fonts.check("700 60px 'Marca'"))
    problemas.push('no cargo Lady Ice (masthead)');
  if (!document.fonts.check("500 30px 'Texto'"))
    problemas.push('no cargo la fuente de texto');

  return problemas;
}
"""


# --------------------------------------------------------------------------

def _guardar_jpg(png_bytes, destino, tamano=None):
    tamano = tamano or (plantilla.ANCHO, plantilla.ALTO)
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    if im.size != tamano:
        im = im.resize(tamano, Image.LANCZOS)
    im.save(destino, "JPEG", quality=CALIDAD, subsampling=0, optimize=True, progressive=True)
    return im.size


def render_sets(ids=None):
    errores_copy = contenido.validar()
    if errores_copy:
        print("Contenido con problemas:")
        for e in errores_copy:
            print("  -", e)
        return 1

    objetivo = [s for s in contenido.SETS if ids is None or s["id"] in ids]
    fallos = []
    generados = 0

    tmp = tempfile.mkdtemp(prefix="lafiore_")

    with sync_playwright() as pw:
        navegador = pw.chromium.launch()
        pagina = navegador.new_page(
            viewport={"width": plantilla.ANCHO, "height": plantilla.ALTO},
            device_scale_factor=ESCALA,
        )
        pagina_historia = navegador.new_page(
            viewport={"width": plantilla.ANCHO, "height": plantilla.ALTO_HISTORIA},
            device_scale_factor=ESCALA,
        )
        pagina_tiktok = navegador.new_page(
            viewport={"width": plantilla.ANCHO, "height": plantilla.ALTO_TIKTOK},
            device_scale_factor=ESCALA,
        )
        for s in objetivo:
            carpeta = os.path.join(SALIDA, "set_%02d" % s["id"])
            os.makedirs(carpeta, exist_ok=True)
            print("SET %02d · %s" % (s["id"], s["seccion"]))

            for nombre, html in plantilla.laminas(s):
                ruta_html = os.path.join(tmp, "set%02d_%s.html" % (s["id"], nombre))
                with open(ruta_html, "w", encoding="utf-8") as f:
                    f.write(html)
                pagina.goto("file:///" + ruta_html.replace("\\", "/"))
                pagina.wait_for_timeout(150)

                problemas = pagina.evaluate(QC_JS)
                etiqueta = "set_%02d/%s" % (s["id"], nombre)
                for p in problemas:
                    fallos.append("%s -> %s" % (etiqueta, p))

                destino = os.path.join(carpeta, nombre + ".jpg")
                png = pagina.locator(".lamina").screenshot(type="png")
                tam = _guardar_jpg(png, destino)
                generados += 1
                estado = "OK " if not problemas else "QC!"
                print("   %s %s  %dx%d  %d KB" % (
                    estado, nombre, tam[0], tam[1], os.path.getsize(destino) // 1024))

            # historia 1080x1920 a partir de la portada
            ruta_html = os.path.join(tmp, "set%02d_historia.html" % s["id"])
            with open(ruta_html, "w", encoding="utf-8") as f:
                f.write(plantilla.historia(s))
            pagina_historia.goto("file:///" + ruta_html.replace("\\", "/"))
            pagina_historia.wait_for_timeout(150)
            for pr in pagina_historia.evaluate(QC_JS):
                fallos.append("set_%02d/historia -> %s" % (s["id"], pr))
            destino = os.path.join(carpeta, "historia.jpg")
            png = pagina_historia.locator(".lamina").screenshot(type="png")
            tam = _guardar_jpg(png, destino, (plantilla.ANCHO, plantilla.ALTO_HISTORIA))
            generados += 1
            print("   OK  historia    %dx%d  %d KB" % (
                tam[0], tam[1], os.path.getsize(destino) // 1024))

            # carrusel vertical para TikTok, en su propia subcarpeta
            carpeta_tt = os.path.join(carpeta, "tiktok")
            os.makedirs(carpeta_tt, exist_ok=True)
            for nombre, html in plantilla.laminas_tiktok(s):
                ruta_html = os.path.join(tmp, "set%02d_tt_%s.html" % (s["id"], nombre))
                with open(ruta_html, "w", encoding="utf-8") as f:
                    f.write(html)
                pagina_tiktok.goto("file:///" + ruta_html.replace("\\", "/"))
                pagina_tiktok.wait_for_timeout(150)
                for pr in pagina_tiktok.evaluate(QC_JS):
                    fallos.append("set_%02d/tiktok/%s -> %s" % (s["id"], nombre, pr))
                destino = os.path.join(carpeta_tt, nombre + ".jpg")
                png = pagina_tiktok.locator(".lamina").screenshot(type="png")
                tam = _guardar_jpg(png, destino, (plantilla.ANCHO, plantilla.ALTO_TIKTOK))
                generados += 1
            print("   OK  tiktok      6 laminas de %dx%d" % (
                plantilla.ANCHO, plantilla.ALTO_TIKTOK))

        navegador.close()

    os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(SALIDA, "captions.json"), "w", encoding="utf-8") as f:
        json.dump(textos_caption.captions(), f, ensure_ascii=False, indent=2)
    with open(os.path.join(SALIDA, "captions_tiktok.json"), "w", encoding="utf-8") as f:
        json.dump(textos_caption.captions_tiktok(), f, ensure_ascii=False, indent=2)

    print("\n%d laminas generadas." % generados)
    if fallos:
        print("\nCONTROL DE CALIDAD - %d problema(s):" % len(fallos))
        for f_ in fallos:
            print("  -", f_)
        return 2
    print("Control de calidad: sin desbordes.")
    return 0


if __name__ == "__main__":
    ids = [int(a) for a in sys.argv[1:]] or None
    sys.exit(render_sets(ids))
