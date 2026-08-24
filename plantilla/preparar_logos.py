# -*- coding: utf-8 -*-
"""
Extrae el sello de La Fiore desde el original vectorial y deja tres versiones
PNG con transparencia real en assets/.

    python plantilla/preparar_logos.py

Origen:  insumos/LA FIORE_Interiorismo V2.pdf, pagina 4
Salida:  assets/logo_dorado.png   sello en dorado #90651F
         assets/logo_blanco.png   sello en blanco (va sobre negro)
         assets/logo_negro.png    sello en negro  #15181A

Por que esta pagina y no el vinilo de acceso: en el vinilo, la palabra FIORE
lleva una sombra desplazada detras de cada letra. Al reducir el sello a un
solo color, la letra y su sombra quedan del mismo tono y la palabra se lee
doble y sucia. La version del interiorismo es de un solo color y trazo
limpio, que es lo que necesita un sello impreso a 100 px de alto.
"""

import os
import sys

import numpy as np
import pymupdf
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, "insumos", "LA FIORE_Interiorismo V2.pdf")
PAGINA = 3                   # indice 0: la pagina 4 del documento
ASSETS = os.path.join(RAIZ, "assets")

LADO = 1400                  # px del PNG final
RASTER = 4200                # ancho al que se rasteriza la pagina antes de recortar
UMBRAL_TINTA = 200           # por debajo de esto es tinta, no papel

DORADO = (0x90, 0x65, 0x1F)
BLANCO = (0xFF, 0xFF, 0xFF)
NEGRO = (0x15, 0x18, 0x1A)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _sello_en_blanco():
    """Rasteriza la pagina del sello, la recorta a la tinta y la deja cuadrada."""
    doc = pymupdf.open(ORIGEN)
    pagina = doc[PAGINA]
    zoom = RASTER / pagina.rect.width
    pix = pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    tinta = np.asarray(im).min(axis=2) < UMBRAL_TINTA
    ys, xs = np.where(tinta)
    if not len(xs):
        raise SystemExit("No se encontro tinta en la pagina %d." % (PAGINA + 1))
    margen = 20
    im = im.crop((max(0, xs.min() - margen), max(0, ys.min() - margen),
                  min(im.width, xs.max() + margen), min(im.height, ys.max() + margen)))

    lado = max(im.size)
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2))
    return lienzo.resize((LADO, LADO), Image.LANCZOS)


def preparar():
    if not os.path.exists(ORIGEN):
        raise SystemExit("Falta el original: %s" % ORIGEN)
    os.makedirs(ASSETS, exist_ok=True)

    base = _sello_en_blanco()
    # tinta negra sobre papel blanco: la luminancia da el alfa directamente
    luz = np.asarray(base).astype(np.float32).max(axis=2) / 255.0
    alfa = np.clip(1.0 - luz, 0, 1)

    for nombre, rgb in (("logo_dorado.png", DORADO),
                        ("logo_blanco.png", BLANCO),
                        ("logo_negro.png", NEGRO)):
        salida = np.zeros((LADO, LADO, 4), dtype=np.uint8)
        salida[..., 0], salida[..., 1], salida[..., 2] = rgb
        salida[..., 3] = (alfa * 255).astype(np.uint8)
        ruta = os.path.join(ASSETS, nombre)
        Image.fromarray(salida, "RGBA").save(ruta)
        print("  %s  %dx%d  %d KB" % (nombre, LADO, LADO, os.path.getsize(ruta) // 1024))

    print("Sello preparado en tres versiones, sin sombra.")


if __name__ == "__main__":
    preparar()
